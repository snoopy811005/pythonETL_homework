import requests
from bs4 import BeautifulSoup
import time
import json
import pandas as pd
from argparse import ArgumentParser

def main():
    #argument
    parser = ArgumentParser()
    parser.add_argument('-k',
                        '--keyword',
                        help='search keyword',
                        type=str,
                        default='data scientist')
    parser.add_argument('-p',
                        '--page',
                        help='how many pages you want to search',
                        type=int,
                        default=1)
    args =parser.parse_args()

    User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40"
    headers = {'User-Agent': User_Agent}

    ss = requests.session()

    jobInfo = []
    for pg in range(args.page):
        parameterDict = {'ro': '0',
                         'kwop': '7',
                         'keyword': args.keyword, # 'Data%20Scientist', # '%20' = ' '
                         'expansionType': 'area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm', # '%2C' = ','
                         'order': '12',
                         'asc': '0',
                         'page': str(pg), # '0',
                         'mode': 's',
                         'jobsource': '2018indexpoc',
                         'langFlag': '0'}
        parameterList = [key+'='+val for key, val in parameterDict.items()]

        url = "https://www.104.com.tw/jobs/search/" + '?' + '&'.join(parameterList)
        # print(url)

        res = ss.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # print(soup)

        # article
        articleList = soup.select('article')
        articleTitleUrlList = list()
        for i in articleList:
            try:
                articleTitle = i.select('a[class="js-job-link"]')[0].text
                articleUrl = "https:" + i.select('a[class="js-job-link"]')[0]['href']
                articleTitleUrlList.append((articleTitle, articleUrl))
                # print(articleTitle)
                # print(articleUrl)
            except:
                pass
                # print(i.select('a[class="js-job-link"]'))
            # print('=============')

        # company, job_title, job_content, job_category
        for articleTitle, articleUrl in articleTitleUrlList:
            print(articleTitle)
            print(articleUrl)

            jobUrl = articleUrl.split('?')[0]
            jobUrlAhead = jobUrl.split('://')[0]
            jobUrlBehindList = jobUrl.split('://')[1].split('/')
            jobUrlBehindList.insert(-1, 'ajax')
            jobUrlBehindList.insert(-1, 'content')
            jobJsUrl = jobUrlAhead + '://' + '/'.join(jobUrlBehindList)
            print('\t' + jobUrl)
            print('\t' + jobJsUrl)

            headers['Referer'] = jobUrl
            articleRes = ss.get(jobJsUrl, headers=headers)
            jsonArticleRes = json.loads(articleRes.text)
            company = jsonArticleRes['data']['header']['custName']
            jobTitle = jsonArticleRes['data']['header']['jobName']
            jobContent = jsonArticleRes['data']['jobDetail']['jobDescription']
            jobCategoryList = [i['description'] for i in jsonArticleRes['data']['jobDetail']['jobCategory']]
            jobInfo.append([jobTitle, company, ','.join(jobCategoryList), jobContent])
            print('\t\t' + company)
            print('\t\t' + jobTitle)
            # print('\t\t' + jobContent)
            print('\t\t' + ','.join(jobCategoryList))
            print('=============')
            time.sleep(1)

    # integrate job information
    columns = ['Job Opening', 'Job Company', 'Job Category', 'Job Content']
    df = pd.DataFrame(data=jobInfo, columns=columns)

    # write to csv
    df.to_csv('./104_Job.csv', index=False)

    # write to excel
    df.to_excel('104_Job.xlsx', index=False, engine='xlsxwriter')



if __name__ == '__main__':
    main()


