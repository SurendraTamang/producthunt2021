import scrapy
import json



class ProducthuntSpider(scrapy.Spider):
    name = 'producthunt'
    headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'Accept': '*/*',
  'Accept-Language': 'en-US,en;q=0.5',
  'content-type': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
}
    graphql_url = 'https://www.producthunt.com/frontend/graphql'
    def start_requests(self):
        payload = json.dumps({
        "operationName": "TopicsPage",
        "variables": {
            "query": None,
            "cursor": "MjA=",
            "order": "most-upvoted"
        },
        "query": "query TopicsPage($cursor:String$query:String$order:String){topics(query:$query first:20 after:$cursor order:$order){edges{node{id ...TopicsPageItemFragment __typename}__typename}pageInfo{endCursor hasNextPage __typename}__typename}}fragment TopicsPageItemFragment on Topic{id name slug description ...TopicFollowButton ...TopicImage __typename}fragment TopicFollowButton on Topic{id slug name isFollowed followersCount ...TopicImage __typename}fragment TopicImage on Topic{name imageUuid __typename}"
        })
        yield scrapy.FormRequest(self.graphql_url, headers=self.headers, body=payload, callback=self.parse_topics, )

    def parse_topics(self, response):
        data_response  = response.json()
        next_page = data_response['data']['topics']['pageInfo'].get('hasNextPage')
        topics_pages = data_response['data']['topics']['edges']
        for topic_page in topics_pages: 
            slug_name = topic_page['node']['slug']
            cursor = "MjAw"
            payload_json = {
                    "operationName": "TopicPage",
                    "variables": {
                        "slug": slug_name,
                        "order": "most-upvoted",
                        "cursor":cursor ,
                        "query": None,
                        "topPostsVariant": "THIS_WEEK",
                        "includeLayout": False
                    },
                    "query": "query TopicPage($slug:String!$cursor:String$query:String$subtopic:ID$order:String$topPostsVariant:TopPostsCardVariant!){topic(slug:$slug){id slug ...MetaTags ...TopicPageHeaderFragment ...TopicPagePostListFragment relatedAd(kind:\"feed\"){...AdFragment __typename}relatedTopics(limit:3){id ...SidebarCardsRelatedTopicsCardFragment __typename}__typename}stories(first:3 order:TRENDING){edges{node{id ...SidebarStoriesCardFragment __typename}__typename}__typename}...TopPostsFragment ...SidebarNewsletterCard}fragment TopPostsFragment on Query{postsTop(preferredVariant:$topPostsVariant){variant posts{id _id name slug tagline ...PostThumbnail __typename}__typename}__typename}fragment PostThumbnail on Post{id name thumbnail{id ...MediaThumbnail __typename}...PostStatusIcons __typename}fragment MediaThumbnail on Media{id imageUuid __typename}fragment PostStatusIcons on Post{name productState __typename}fragment SidebarStoriesCardFragment on AnthologiesStory{id slug title headerImageUuid __typename}fragment SidebarCardsRelatedTopicsCardFragment on Topic{id slug name imageUuid description __typename}fragment SidebarNewsletterCard on Query{newsletters(first:1){edges{node{id slug subject primarySection{imageUuid __typename}__typename}__typename}__typename}__typename}fragment MetaTags on SEOInterface{id meta{canonicalUrl creator description image mobileAppUrl oembedUrl robots title type author authorUrl __typename}__typename}fragment AdFragment on AdChannel{id post{id slug name updatedAt commentsCount ...PostVoteButton __typename}ctaText dealText name tagline thumbnailUuid url __typename}fragment PostVoteButton on Post{_id id featuredAt updatedAt createdAt disabledWhenScheduled hasVoted ...on Votable{id votesCount __typename}__typename}fragment TopicPageHeaderFragment on Topic{id name description ...TopicFollowButton ...FacebookShareButtonFragment topPosts:posts(first:3 order:\"most-upvoted\"){edges{node{id name slug ...PostThumbnail __typename}__typename}__typename}__typename}fragment TopicFollowButton on Topic{id slug name isFollowed followersCount ...TopicImage __typename}fragment TopicImage on Topic{name imageUuid __typename}fragment FacebookShareButtonFragment on Shareable{id url __typename}fragment TopicPagePostListFragment on Topic{name slug posts(first:20 after:$cursor query:$query subtopic:$subtopic order:$order){edges{node{id ...PostItem ...TopicPageReviewRatingFragment __typename}__typename}pageInfo{endCursor hasNextPage __typename}__typename}__typename}fragment PostItem on Post{id _id commentsCount name shortenedUrl slug tagline updatedAt pricingType topics(first:1){edges{node{id name slug __typename}__typename}__typename}...PostThumbnail ...PostVoteButton __typename}fragment TopicPageReviewRatingFragment on Post{id slug reviewsWithBodyCount __typename}"
                    }

            yield scrapy.FormRequest(self.graphql_url, headers=self.headers, body=json.dumps(payload_json), callback=self.get_posts, meta={'slug_name': slug_name, 'payload_json':payload_json})

       
        if next_page:
            cursor = data_response['data']['topics']['pageInfo'].get('endCursor')
            payload = json.dumps({
                "operationName": "TopicsPage",
                "variables": {
                    "query": None,
                    "cursor": cursor,
                    "order": "most-upvoted"
                },
                "query": "query TopicsPage($cursor:String$query:String$order:String){topics(query:$query first:20 after:$cursor order:$order){edges{node{id ...TopicsPageItemFragment __typename}__typename}pageInfo{endCursor hasNextPage __typename}__typename}}fragment TopicsPageItemFragment on Topic{id name slug description ...TopicFollowButton ...TopicImage __typename}fragment TopicFollowButton on Topic{id slug name isFollowed followersCount ...TopicImage __typename}fragment TopicImage on Topic{name imageUuid __typename}"
            })
            yield scrapy.FormRequest(self.graphql_url, headers=self.headers, body=payload, callback=self.parse_topics, )

    def get_posts(self, response):
        json_file = response.json()
        next_page_info = json_file['data']['topic']['posts']['pageInfo']
        next_page = next_page_info.get('hasNextPage')
        posts = json_file['data']['topic']['posts']['edges']
        for post in posts:
            slug_name = post['node']['slug']
            payload = json.dumps({
            "operationName": "PostPage",
            "variables": {
                "slug": slug_name,
                "topPostsVariant": "TODAY"
            },
            "query": "query PostPage($slug:String!$topPostsVariant:TopPostsCardVariant!){post(slug:$slug){_id id slug name tagline trashedAt isAvailable pricingType productLinks{id redirectPath __typename}relatedAd(kind:\"sidebar\"){...AdFragment __typename}...CollectButtonFragment ...FacebookShareButtonFragment ...MetaTags ...PostBadgesFragment ...PostPageActionsFragment ...PostPageDescription ...PostPageGallery ...PostPageGetItButtons ...PostPageLaunchTips ...PostPageModerationReason ...PostPageSocialLinks ...PostPageTimestampFragment ...PostStatusIcons ...PostThumbnail ...PostVoteButton ...TopicFollowButtonList ...PostPageMakersCard ...PostCommentInput ...PostPageVotersFragment ...PostPageUpvoteBarFragment ...ScheduledNoticeFragment ...ModerationToolsFragment ...LaunchDayNoticeFragment ...LaunchDashMessageFragment ...EmbedButtonFragment ...EmbedBadgeMessageFragment ...StructuredDataFromPost ...PostPageQuestionsFragment __typename}viewer{id deviceType ...NewsletterSubscribeFormPopupFragment __typename}dismissed(dismissableGroup:\"cards\" dismissableKey:\"EmailSubscribeCard\"){id isDismissed dismissableGroup dismissableKey __typename}...TopPostsFragment}fragment PostPageActionsFragment on Post{id _id name slug userId url canManage __typename}fragment PostPageDescription on Post{_id id slug description isMaker canComment canManage promo{text code __typename}makers{id __typename}__typename}fragment PostPageGallery on Post{id slug canManage createdAt updatedAt media{id originalHeight originalWidth ...MediaCarouselFragment __typename}__typename}fragment MediaCarouselFragment on Media{id imageUuid mediaType originalHeight originalWidth metadata{url videoId platform __typename}__typename}fragment PostPageGetItButtons on Post{id isAvailable productLinks{id redirectPath storeName websiteName devices __typename}__typename}fragment PostPageLaunchTips on Post{id _id canComment commentsCount createdAt featuredAt makerInviteUrl slug name isMaker isHunter url __typename}fragment PostPageModerationReason on Post{moderationReason{reason moderator{id name headline username __typename}__typename}__typename}fragment PostPageSocialLinks on Post{id angellistUrl facebookUrl githubUrl instagramUrl mediumUrl twitterUrl isAvailable __typename}fragment PostPageTimestampFragment on Post{id disabledWhenScheduled createdAt featuredAt __typename}fragment PostPageMakersCard on Post{id canManage slug user{id name headline username ...UserImage __typename}makers{id name headline username ...UserImage __typename}__typename}fragment UserImage on User{_id id name username avatarUrl headline isViewer ...KarmaBadge __typename}fragment KarmaBadge on User{karmaBadge{kind score __typename}__typename}fragment CollectButtonFragment on Post{id name isCollected __typename}fragment PostStatusIcons on Post{name productState __typename}fragment PostThumbnail on Post{id name thumbnail{id ...MediaThumbnail __typename}...PostStatusIcons __typename}fragment MediaThumbnail on Media{id imageUuid __typename}fragment PostVoteButton on Post{_id id featuredAt updatedAt createdAt disabledWhenScheduled hasVoted ...on Votable{id votesCount __typename}__typename}fragment FacebookShareButtonFragment on Shareable{id url __typename}fragment TopicFollowButtonList on Topicable{id topics{edges{node{id ...TopicFollowButton __typename}__typename}__typename}__typename}fragment TopicFollowButton on Topic{id slug name isFollowed followersCount ...TopicImage __typename}fragment TopicImage on Topic{name imageUuid __typename}fragment MetaTags on SEOInterface{id meta{canonicalUrl creator description image mobileAppUrl oembedUrl robots title type author authorUrl __typename}__typename}fragment PostCommentInput on Post{_id id canManage __typename}fragment AdFragment on AdChannel{id post{id slug name updatedAt commentsCount ...PostVoteButton __typename}ctaText dealText name tagline thumbnailUuid url __typename}fragment PostBadgesFragment on Post{id badges{edges{node{...on TopPostBadge{id position period date __typename}...on GoldenKittyAwardBadge{id category year __typename}__typename}__typename}__typename}...EmbedButtonFragment __typename}fragment EmbedButtonFragment on Post{id slug __typename}fragment PostPageVotersFragment on Post{id votesCount __typename}fragment PostPageUpvoteBarFragment on Post{id name tagline ...PostVoteButton ...PostThumbnail ...PostPageGetItButtonFragment __typename}fragment PostPageGetItButtonFragment on Post{id isAvailable productState productLinks{id __typename}...PostPageGetItButtons ...ProductUnavailableButtonFragment __typename}fragment ProductUnavailableButtonFragment on Post{id __typename}fragment ScheduledNoticeFragment on Post{id createdAt featuredAt __typename}fragment NewsletterSubscribeFormPopupFragment on Viewer{id showCookiePolicy ...SubscribeToNewsletterFormViewer __typename}fragment SubscribeToNewsletterFormViewer on Viewer{id email hasNewsletterSubscription __typename}fragment ModerationToolsFragment on Post{id name slug __typename}fragment LaunchDayNoticeFragment on Post{id slug createdAt isMaker isHunter __typename}fragment LaunchDashMessageFragment on Post{id slug isMaker isHunter createdAt __typename}fragment EmbedBadgeMessageFragment on Post{id embedBadgeMessage{title tagline url __typename}__typename}fragment StructuredDataFromPost on Post{id structuredData __typename}fragment TopPostsFragment on Query{postsTop(preferredVariant:$topPostsVariant){variant posts{id _id name slug tagline ...PostThumbnail __typename}__typename}__typename}fragment PostPageQuestionsFragment on Post{id questions(first:3){edges{node{id slug title __typename}__typename}__typename}__typename}"
            })
            headers = {
            'authority': 'www.producthunt.com',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': '*/*',
            'content-type': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://www.producthunt.com',
            }
        yield scrapy.FormRequest(url=self.graphql_url, body=payload, headers=headers, callback=self.parse_details)

        if next_page == True:
            cursor = next_page_info.get('endCursor')
            payload_json = response.meta['payload_json']
            new_payload_json = payload_json.copy()
            new_payload_json['variables']['cursor'] = cursor
            yield scrapy.FormRequest(self.graphql_url, headers=self.headers, body=json.dumps(new_payload_json), callback=self.get_posts, meta={'payload_json':payload_json})
        
    def parse_details(self, response):
        json_file = response.json()
        yield json_file['data']

