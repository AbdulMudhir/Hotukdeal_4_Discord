import discord, requests, re
from bs4 import BeautifulSoup as bs
from discord.ext import tasks

bot = discord.Client()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
}


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    class Hotukdeal:

        def __init__(self, link, current_channel):
            self.link = link
            self.channel = current_channel
            self.deal_logs = deal_logs = {}

        async def get_multiple_deals(self):

            for i in range(1,4): #number of pages to go through

                link = f'{self.link}{i}'

                category = requests.get(link, headers=headers)  # download html

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

            return self.deal_logs.items()

        async def get_posted_deals(self):

            chat_logs = {}

            msg = await self.channel.history(limit=500).flatten()

            for messages in msg:
                embed_content = messages.embeds
                for content in embed_content:
                    title = content.title  # title of the embed
                    chat_logs[title] = messages.id

            return chat_logs

        async def _filter_inventory(self):

            retrieve_log = await self.get_posted_deals()

            self.filtered_deals = {item: value for item, value in await self.get_multiple_deals() if not value[-1]}

            for item, message_id in retrieve_log.items():
                if item in self.filtered_deals.keys():
                    continue
                else:
                    #print('Removed', item)
                    msg = await self.channel.fetch_message(message_id)
                    await msg.delete()

            await self.send_deals()
            #self.deal_logs.clear()


        async def send_deals(self):

            retrieve_log = await self.get_posted_deals()

            for item, value in self.filtered_deals.items():
                if item in retrieve_log.keys():
                    continue
                else:
                    embed = discord.Embed(
                        title=f'{item}',
                        description=f'{value[8]} [Read more]({value[7]})',
                        colour=2470660,
                        url=value[6], )

                    embed.set_footer(text=value[2], icon_url=value[3])
                    embed.set_thumbnail(url=value[1])
                    embed.add_field(name='Price', value=value[0])
                    embed.add_field(name="Hot Meter", value=value[5])
                    embed.add_field(name='Comments' if int(value[4]) > 1 else 'Comment', value=value[4])

                    await self.channel.send(embed=embed)

        async def _filter_duplicates(self):

            msg = await self.channel.history(limit=100).flatten()

            await self.channel.delete_messages(msg)

    homepage = Hotukdeal('https://www.hotukdeals.com/hot?page=', bot.get_channel(your_channel_id))
    gaming = Hotukdeal('https://www.hotukdeals.com/tag/gaming?page=', bot.get_channel(your_channel_id))
    electronics = Hotukdeal('https://www.hotukdeals.com/tag/electronics?page=', bot.get_channel(your_channel_id))
    steam = Hotukdeal('https://www.hotukdeals.com/tag/steam-hot?page=', bot.get_channel(your_channel_id))

    @tasks.loop(seconds=3600)  # when to check for deals
    async def start_sending():

        await homepage._filter_inventory()
        homepage.deal_logs.clear() # clearing deal logs to remove any outdated deals
        await gaming._filter_inventory()
        gaming.deal_logs.clear()# clearing deal logs to remove any outdated deals
        await electronics._filter_inventory()
        electronics.deal_logs.clear()# clearing deal logs to remove any outdated deals
        await steam._filter_inventory()
        steam.deal_logs.clear()# clearing deal logs to remove any outdated deals

    start_sending.start() #stat the loop


bot.run('Your Token')
