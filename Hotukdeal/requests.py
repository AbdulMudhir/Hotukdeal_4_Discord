import requests, re
from bs4 import BeautifulSoup as bs

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
}


class Hud:

    def __init__(self, link, current_channel = None):
        self.link = link
        self.channel = current_channel
        self.deal_logs = deal_logs = {}

    def get_multiple_deals(self):

        category = requests.get(self.link, headers=headers)  # download html

        soup = bs(category.text, 'html.parser')  # parse html to be readable

        deal_box = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['threadGrid'])

        for deals in deal_box:
            """check if a  deal has expired"""
            if re.search(
                    r'cept-vote-box vote-box vote-box--muted space--h-2 border border--color-borderGrey bRad--a text--color-grey space--mr-3',
                    str(deals)):
                expired = True
            else:
                expired = False

            try:
                category_img = soup.find('img',
                                         class_='img img--type-collection img--square-xl img--toW2-square-m img--noBorder boxShadow')[
                    'src']
            except TypeError:
                category_img = 'https://cdn0.iconfinder.com/data/icons/user-interface-vol-5-4/66/2-512.png'

            try:
                title = deals.find('strong', class_='thread-title').a['title']

            except (TypeError, AttributeError):
                title = None
                continue

            try:
                hot = deals.find('span', class_='cept-vote-temp').text
            except:
                hot = None

            try:
                image = deals.img['src']
            except KeyError:
                image = ''.join(re.search('https:.+?\.(jpg|png)', str(deals.img)).group(0).split('\\'))

            try:
                price = deals.find('span',
                                   class_='thread-price text--b vAlign--all-tt cept-tp size--all-l size--fromW3-xl').text
            except AttributeError:
                price = 'Free'
                pass

            try:
                comment = deals.find('span', class_='footerMeta-actionSlot').text

            except AttributeError:
                pass

            try:
                direct_link = deals.find('span', class_='iGrid-item').a['href']
            except (TypeError, AttributeError):
                direct_link = \
                    deals.find('div',
                               class_='width--fromW2-6 space--fromW2-r-1 space--t-1 space--fromW2-t-0').a[
                        'href']

            try:
                forum = deals.find('strong', class_='thread-title').a['href']
            except TypeError:
                print('none')

            try:
                summary = deals.find('div', class_='userHtml userHtml-content').div.text.split('\t')[0]
                if not summary:
                    summary = deals.find('div', class_='cept-description-container').text
            except TypeError:
                pass

            try:
                times = deals.find('span', class_='hide--fromW3').text
            except TypeError:
                pass

            if title not in self.deal_logs.keys():
                self.deal_logs[title] = [price, image, times, category_img, comment, hot, direct_link,
                                         forum,
                                         summary, expired]

