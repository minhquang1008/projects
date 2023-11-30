import os
import datetime as dt

from PIL import Image
from os.path import join

from color import Color
import data


def run(domain, dataDate: dt.datetime):
    os.chdir(r"D:\ProjectCompany\DataAnalytics\automation\brokerage\dashboardBOM")

    if domain == 'CoSo':
        from coso import dashboard
        padColor = Color.LIGHTBLUE
        dashboardType = 'Underlying'
    elif domain == 'PhaiSinh':
        from phaisinh import dashboard
        padColor = Color.LIGHTGREEN
        dashboardType = 'Derivatives'
    else:
        raise ValueError('Invalid domain, it must be either "CoSo" or "PhaiSinh"')

    dailyData = data.Daily(dataDate=dataDate, domain=domain)
    monthlyData = data.MTD(dataDate=dataDate, domain=domain)
    yearlyData = data.YTD(dataDate=dataDate, domain=domain)

    # Instantiate
    dailyDashboards = dashboard.Daily(dataContainer=dailyData)
    monthlyDashboards = dashboard.MTD(dataContainer=monthlyData)
    yearlyDashboards = dashboard.YTD(dataContainer=yearlyData)

    # Draw
    dailyDashboards.draw()
    monthlyDashboards.draw()
    yearlyDashboards.draw()

    dailyDashboard = dailyDashboards.artist.product
    monthlyDashboard = monthlyDashboards.artist.product
    yearlyDashboard = yearlyDashboards.artist.product

    commonWidth = yearlyDashboard.width
    commonHeight = yearlyDashboard.height
    pad = 10
    result = Image.new(
        mode='RGB',
        size=(commonWidth + pad + commonWidth + pad + commonWidth, commonHeight),
        color=padColor,
    )
    for i, dashboardImage in enumerate([dailyDashboard, monthlyDashboard, yearlyDashboard]):
        result.paste(
            im=dashboardImage,
            box=((commonWidth + pad) * i, 0),
        )
    rootDir = r"C:\Users\quangpham\Desktop"
    if not os.path.isdir(join(rootDir, f"{dataDate.year}")):
        os.mkdir((join(rootDir, f"{dataDate.year}")))
    if not os.path.isdir(join(rootDir, f"{dataDate.year}", f"{dataDate.strftime('%Y.%m.%d')}")):
        os.mkdir((join(rootDir, f"{dataDate.year}", f"{dataDate.strftime('%Y.%m.%d')}")))

    savedPath = join(rootDir, f"{dataDate.year}", f"{dataDate.strftime('%Y.%m.%d')}")
    imgName = fr"Brokerage_{dashboardType}_{dataDate.strftime('%Y%m%d')}.png"
    imgPath = join(savedPath, imgName)
    result.save(imgPath)
    del result  # memory clearance


run('CoSo', dt.datetime(2023,5,25))
# run('PhaiSinh', dt.datetime(2023,5,25))
