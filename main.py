import tweepy
import base64
from requests.auth import HTTPBasicAuth
import requests

# Twitter系の必要情報--------------------------------------------------
CONSUMER_KEY =''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
TW_USER_ID = "" #取得したいユーザーのユーザーIDを代入
# はてなブログの必要情報------------------------------------------------
HATENA_ID = "" #はてなIDをいれる
BLOG_ID = 'xxx.hatenablog.com'; #ブログIDをいれる 
API_KEY = ''; #APIキーをいれる
#-------------------------------------------------------------------

# 日付とツイートの情報を持つクラス
class Entry:
    def __init__(self, date):
        self.date = date 
        self.body = [] 
    
    def append_tweet(self, tweet):
        self.body.append(tweet)
    
    def get_date(self):
      return self.date

    # tweetsは日付の新しい順なので、古い順に並べ替えたいときにorder=1にします。
    def get_content(self, order=1):
      if order == 1: 
        return '\n'.join(list(reversed(self.body)))
      else:
        return '\n'.join(self.body)

#ツイートを取得し、返します。
def get_tweets(user_id, count=10):
  # Twitterオブジェクトの生成
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  tweets = []

  # 大量に取りたい場合、最大3200件
  # for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
  #   tweets.append(status)
  tweets = api.user_timeline(user_id, count=count, page=1)
  return tweets
 
# はてなブログ用に記事のbodyを作成します。
def generate_entries(user_id, tweets):
  tweet_url_str = 'https://twitter.com/' + user_id + '/status/'
  date_format = '%Y-%m-%d'
  date = ''
  entries = []

  # 日付が変わるまでツイートを取得して保存しておく
  # 日付が変わったら、前の日付を元にentryクラスを作成して、
  # 保存しておいたツイートをentryクラスの中に保存する
  for tweet in tweets:
    if date == '':
      date = tweet.created_at.strftime(date_format)
      entry = Entry(date)

    if date != tweet.created_at.strftime(date_format):
      date = tweet.created_at.strftime(date_format)
      entries.append(entry)
      entry = Entry(date)
    
    entry.append_tweet('<p>[' + tweet_url_str + tweet.id_str + ':embed#' + tweet.text + ']</p>')

  return entries

# はてなブログ用に投稿します。 
def post(title, content, updated, category):
  url = 'https://blog.hatena.ne.jp/' + HATENA_ID + '/' + BLOG_ID + '/atom/entry'

  xml = '<?xml version="1.0" encoding="utf-8"?><entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app"><title>' \
      + title + '</title><author><name>' \
      + HATENA_ID + '</name></author><content type="text/plain">' \
      + content + '</content><updated>' \
      + updated + '</updated><category term="' \
      + category + '" /><app:control><app:draft>no</app:draft></app:control></entry>'

  headers = {
    'method' : 'post',
    'contentType' : 'application/xml',
  }
  r = requests.post(url, data=xml.encode(), headers=headers, auth=HTTPBasicAuth(HATENA_ID, API_KEY))

# 複数件、投稿するためのロジック
# 記事のタイトルなどを変えたい時は適宜編集します。
def post_entries(entries):
  for entry in entries:
    title = entry.date + "の練習記録" # 記事のタイトル
    updated = entry.get_date() + "T23:59:59" # 記事の投稿日時
    content = entry.get_content()
    category = "英語学習記録" # 記事のカテゴリ。複数対応はまだしていません。
    post(title, content, updated, category)

#メインのロジックが書かれているところ
def main():
  # 任意のidのtweetをcountの数だけ取得
  tweets = get_tweets(TW_USER_ID, count=10)
  # 取得したtweetをブログ用に整えます 
  entries = generate_entries(TW_USER_ID, tweets)
  # はてなブログに投稿します 
  for entry in entries:
    post_entries(entries)

if __name__ == '__main__':
  main()