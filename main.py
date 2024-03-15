import asyncio
import aiohttp
from flask import Flask, render_template, request
import re

app = Flask(__name__, template_folder='templates')

class Share:
    async def get_token(self, session, cookies):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="103", "Chromium";v="103", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'cookie': cookies
        }
        async with session.get('https://business.facebook.com/content_management', headers=headers) as response:
            data = await response.text()
            access_token = 'EAAG' + re.search('EAAG(.*?)","', data).group(1)
            return access_token, cookies

    async def share(self, session, token, cookie, post_id, share_count):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'accept-encoding': 'gzip, deflate',
            'host': 'graph.facebook.com',
            'cookie': cookie
        }
        count = 1
        while count < share_count:
            async with session.post(f'https://graph.facebook.com/me/feed?link=https://www.facebook.com/{post_id}&published=0&access_token={token}', headers=headers) as response:
                data = await response.json()
                if 'id' in data:
                    print(f"[ {count}/{share_count} ] - {data['id']} - booster share")
                    count += 1
                else:
                    print("[ BLOCK ]: cookie is blocked, ctrl c to exit !!!!")
                    print(f"End: {count} ok?")
                    break

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cookie = request.form.get('cookie')
        post_id = request.form.get('id')
        share_count = int(request.form.get('share_count'))

        async def main(num_tasks):
            async with aiohttp.ClientSession() as session:
                share = Share()
                token, _ = await share.get_token(session, cookie)
                tasks = []
                for _ in range(num_tasks):
                    task = asyncio.create_task(share.share(session, token, cookie, post_id, share_count))
                    tasks.append(task)
                await asyncio.gather(*tasks)

        asyncio.run(main(2))
        return 'Share complete! pls follow Shiki Machina'

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='5000')
