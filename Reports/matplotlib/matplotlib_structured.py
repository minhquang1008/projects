import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from abc import ABC, abstractmethod
import mplcyberpunk
import io
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import datetime
from datawarehouse import connect_DWH_CoSo


class Chart(ABC):
    def __init__(self) -> None:
        self.__data = None
        self.colors = ['#1D40CC', '#4167a4', '#FF7700', '#f99c4b']
        self.textColor = '#fcfdfe'

    @property
    def data(self) -> pd.DataFrame:
        return self.__data

    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        self.__data = data

    @abstractmethod
    def draw(self):
        pass

    def __drawTransparentBarChart(self, ind):
        return plt.bar(
            ind, self.data['target'],
            align='center', color='white',
            fill=True, width=0.6,
            edgecolor='grey', linewidth=0.5)

    def __drawNormalBarChart(self, ind, colors):
        return plt.bar(ind, self.data['performance'], align='center', color=colors, width=0.5)

    @staticmethod
    def __reformatNumberYAxis():
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
        plt.yticks(fontsize=20)

    def __addLabelsXAxis(self, ind):
        for i in range(len(ind)):
            plt.text(
                i, self.data['performance'][i]//10,
                "{:,}".format(self.data['performance'][i]),
                ha='center',
                rotation=90,
                fontsize=14)

    def __drawHLine(self, bars, color):
        x_start = np.array([plt.getp(item, 'x') for item in bars])
        x_end = x_start+[plt.getp(item, 'width') for item in bars]
        plt.hlines(self.data['target'], x_start, x_end, color=color, edgecolor=color, linewidth=3)

    def drawBarChart(self):
        # chỉnh màu của line x y, và label thành màu gần màu trắng
        plt.rcParams.update({'text.color': self.textColor,
                             'axes.labelcolor': self.textColor})
        ind = np.arange(len(self.data['month']))
        # chỉnh màu theo ratio
        ratio = self.data['performance']/self.data['target']
        colors = [self.colors[2] if i < 1 else self.colors[0] for i in ratio]
        # size của biểu đồ
        fig = plt.figure(figsize=(14, 7))
        # subplot
        ax = fig.add_subplot()
        # ẩn các cột trái phải và bên trên
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(self.textColor)
        ax.tick_params(axis='x', colors=self.textColor)
        ax.tick_params(axis='y', colors=self.textColor)
        # ẩn dấu gạch - cột x cột y
        plt.tick_params(
            axis='both',
            left=False,
            top=False,
            right=False,
            bottom=False,
            labelleft=True,
            labeltop=False,
            labelright=False,
            labelbottom=True)
        # tạo legend
        color_map = {'Actual>=100% of Target': self.colors[0],
                     'Actual<100% of Target': self.colors[2],
                     'Target': self.colors[0]}
        labels = list(color_map.keys())
        handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[label]) for label in labels]
        plt.xticks(ind, self.data['month'], fontsize=14)
        plt.legend(handles, labels, frameon=False, ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.05), fontsize=20)
        # tên biểu đồ
        plt.title("Actual Sales vs Target")
        # vẽ bar chart trong suốt để tạo đường kẻ bên ngoài các cột
        transparentBarChart = self.__drawTransparentBarChart(ind)
        # đè bar chart thật lên trên
        normalBarChart = self.__drawNormalBarChart(ind, colors)
        # chỉnh format, fontsize số cột y
        self.__reformatNumberYAxis()
        # add label vào từng bar
        self.__addLabelsXAxis(ind)
        # vẽ hline đè
        self.__drawHLine(transparentBarChart, 'w')
        self.__drawHLine(normalBarChart, self.colors[0])
        return fig

    def drawCurvedBar(self):
        r = 1.5
        r_inner = 0.4
        categories = self.data['criteria']
        percent = self.data['completed']
        colors = [self.colors[3] if i < 50 else self.colors[2] if 100 > i >= 50 else self.colors[1] for i in
                  percent]
        # số lượng tiêu chí input vào biểu đồ
        n = len(self.data)
        # tỷ lệ hoàn thành nếu lớn hơn 100 thì gán là 100, lớn hơn 100 ko vẽ đc piechart
        for i in percent:
            i = 100 if i > 100 else i
        percent_circle = max(percent) / 100
        # tính chiều rộng mỗi ring
        w = (r - r_inner) / n
        # tạo figure, axis
        fig, ax = plt.subplots(figsize=(7, 7))
        # vẽ biểu đồ
        for i in range(n):
            radius = r - i * w
            p = lambda p: 0.91 if i == 0 else 0.89 if i == 1 else 0.86 if i == 2 else 0.8
            ax.pie([(percent[i] / max(percent) * percent_circle), (1 - (percent[i] / max(percent) * percent_circle))],
                   radius=radius, startangle=90,
                   counterclock=False,
                   colors=[colors[i], 'white'], labeldistance=None,
                   wedgeprops={'width': w, 'edgecolor': 'white', 'linewidth': 9, 'alpha': 1},
                   autopct='%.f%%', textprops={'color': 'w', 'weight': 'bold', 'fontsize': 18}, pctdistance=p(i))
            ax.text(0, radius - w / 2, f'{categories[i]}', ha='right', va='center', fontsize=20, weight='bold',
                    color=self.textColor)
        plt.tight_layout()
        return fig

    def drawPieChart(self):
        data = np.array([self.data, 100-self.data])
        fig = plt.figure(figsize=(7.5, 7.5))
        myexplode = [0.1, 0]
        color = [self.colors[2], self.colors[0]]
        label = ['{}%'.format(self.data), '']
        plt.pie(data, explode=myexplode, colors=color, labels=label, labeldistance=0.5,
                textprops={'fontsize': 35, 'color': self.textColor})
        return fig

    def drawDonutChart(self):
        # data mẫu
        # [40000, 50000, 70000, 54000]
        # vẽ Pie Chart
        fig = plt.figure(figsize=(13, 6))
        broker = ['Broker A', 'Broker B', 'Broker C', 'remaining']
        colors = [self.colors[0], self.colors[1], self.colors[2], self.colors[3]]
        plt.pie(self.data, colors=colors, autopct='%1.0f%%', textprops={'fontsize': 35, 'color': self.textColor},
                radius=1.5)
        plt.pie(self.data, colors=['white']*4, wedgeprops={'edgecolor': 'white'}, radius=0.55)
        leg = plt.legend(broker, frameon=False, loc='upper left', bbox_to_anchor=(1.2, 1.2), prop={'size': 26})
        for text in leg.get_texts():
            text.set_color(self.textColor)
        return fig

    def drawLineChart(self):
        plt.style.use("cyberpunk")
        # define data values
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        x = self.data['date']  # X-axis points
        y = self.data['unit']  # Y-axis points
        plt.ylabel("Total Units", fontsize=20)
        ax.grid(axis='y', color='#fcfdfe')
        # ax.set_xticks(x)
        plt.xticks(rotation=45)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['bottom'].set_color(self.textColor)
        ax.tick_params(axis='x', colors=self.textColor, labelsize=16)
        ax.tick_params(axis='y', colors=self.textColor, labelsize=16)
        reformat = mdates.DateFormatter('%b-%y')
        ax.xaxis.set_major_formatter(reformat)
        plt.tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=True, labeltop=False,
                        labelright=False, labelbottom=True)
        plt.plot(x, y, color=self.colors[2])
        mplcyberpunk.make_lines_glow()
        mplcyberpunk.add_underglow()
        return fig
        # plt.show()  # display

    def drawSimpleBarChart(self):
        fig = plt.figure(figsize=(3, 8))
        ax = fig.add_subplot()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_frame_on(False)
        ax.axes.set_xticks([])
        ax.axes.set_yticks([])
        # create data
        y1 = self.data[0]
        y2 = self.data[1]
        plt.text(-0.05, max(y1, y2)+0.2, 'VND million', fontsize=30)
        width = 0.1
        plt.text(0, y1 * 0.85, "{:,}".format(y1), ha='center', fontsize=30, color=self.textColor)
        plt.text(0.1, y2 * 0.85, "{:,}".format(y2), ha='center', fontsize=30, color=self.textColor)
        # plot data in grouped manner of bar type
        plt.bar(0, [y1], width, color=self.colors[2])
        plt.bar(0.1, [y2], width, color=self.colors[0])
        plt.legend(['Actual', 'Target'], loc=8, bbox_to_anchor=(0.5, -0.18), ncol=1, frameon=False, fontsize=22)
        plt.tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=True, labeltop=False,
                        labelright=False, labelbottom=True)
        return fig

    @staticmethod
    def findOrdinal(date: str):
        # connection
        test_date = datetime.strptime(date, '%Y-%m-%d')
        # query
        df = pd.read_sql(
            f'''
            SELECT * FROM [Date]
            WHERE MONTH([Date]) LIKE '{test_date.month}' AND 
            YEAR([Date]) LIKE'{test_date.year}' AND 
            [Work] = 1
            ''', connect_DWH_CoSo)
        df = df.sort_values('Date', ignore_index=True)
        test_date_list = df['Date']
        closest_dict = {
            (test_date - date).days: date
            for date in test_date_list}
        res = closest_dict[min([i for i in closest_dict.keys() if i >= 0])]
        passed_days = df['Date'][df['Date'] == res].index.item() + 1
        working_days = len(df)
        return passed_days, working_days

    @staticmethod
    def findMonth(date: str):
        test_date = datetime.strptime(date, '%Y-%m-%d')
        passed_days = test_date.month
        remaining_days = 12 - passed_days
        return passed_days, remaining_days

    def drawMonthProgress(self, date: str):
        passed_days, working_days = self.findOrdinal(date)
        remaining_days = working_days - passed_days
        df = pd.DataFrame([[passed_days, remaining_days]], columns=['passed', 'remaining'])
        passed_days = df['passed'].iloc[0]
        ax = df.plot.barh(
            stacked=True,
            legend=False,
            mark_right=True,
            color=['#26c5f4', '#24324d'],
            figsize=(12, 3))
        plt.xlim(-2, 22)
        plt.ylim(-2, 2)
        plt.text((passed_days+remaining_days)/2, 1, f"{passed_days}/{working_days}",
                 va='center', ha='center', color=self.textColor, fontsize=30, weight='bold')
        fig = ax.get_figure()
        circle1 = patches.Ellipse((0, 0), 0.478, 1, angle=90, color='#26c5f4')
        circle2 = patches.Ellipse((working_days, 0), 0.478, 1, angle=90, color='#24324d')
        circle3 = patches.Ellipse((passed_days, 0), 0.478, 1, angle=90, color='#26c5f4')
        ax.add_artist(circle1)
        ax.add_artist(circle2)
        ax.add_artist(circle3)
        plt.axis('off')
        return fig

    def drawYearProgress(self, date: str):
        passed_days, remaining_days = self.findMonth(date)
        df = pd.DataFrame([[passed_days, remaining_days]], columns=['passed', 'remaining'])
        passed_days = df['passed'].iloc[0]
        ax = df.plot.barh(
            stacked=True,
            legend=False,
            mark_right=True,
            color=['#26c5f4', '#24324d'],
            figsize=(12, 3))
        plt.xlim(-2, 22)
        plt.ylim(-2, 2)
        plt.text((passed_days+remaining_days)/2, 1, f"{passed_days}/12",
                 va='center', ha='center', color=self.textColor, fontsize=30, weight='bold')
        fig = ax.get_figure()
        circle1 = patches.Ellipse((0, 0), 0.478, 1, angle=90, color='#26c5f4')
        circle2 = patches.Ellipse((12, 0), 0.478, 1, angle=90, color='#24324d')
        circle3 = patches.Ellipse((passed_days, 0), 0.478, 1, angle=90, color='#26c5f4')
        ax.add_artist(circle1)
        ax.add_artist(circle2)
        ax.add_artist(circle3)
        plt.axis('off')
        return fig


class ImageWriter:
    def __init__(self, line1Figures: list, line2Figures: list,
                 line3Figures: list, line4Figures: list, line5Figures: list):
        self.line1Figures = line1Figures
        self.line2Figures = line2Figures
        self.line3Figures = line3Figures
        self.line4Figures = line4Figures
        self.line5Figures = line5Figures
        self.backGround = Image.open("background.png")
        self.theCrown = Image.open("crown.png")
        self.theStar = Image.open("star.png")
        self.theRedTriangle = Image.open("red_triangle.png")
        self.theGreenTriangle = Image.open("green_triangle.png")

    # đổi figure thành image
    @staticmethod
    def __figToImg(fig):
        buf = io.BytesIO()
        fig.savefig(buf, dpi=180, transparent=True)
        buf.seek(0)
        img = Image.open(buf)
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        return img

    @staticmethod
    # hàm để ghép 3 hình lại với nhau
    def mergeImage(imageList):
        images = [x for x in imageList]
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_img = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for im in images:
            new_img.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        # new_im.save('test.png')
        return new_img

    def writeImage(self):

        big_font = ImageFont.truetype("arial.ttf", 110)
        tiny_font = ImageFont.truetype("arial.ttf", 80)
        self.backGround.paste(self.__figToImg(self.line1Figures[0]), (100, 400), self.__figToImg(self.line1Figures[0]))
        self.backGround.paste(self.__figToImg(self.line1Figures[1]), (3100, 500), self.__figToImg(self.line1Figures[1]))
        self.backGround.paste(self.__figToImg(self.line1Figures[2]), (4800, 500), self.__figToImg(self.line1Figures[2]))
        self.backGround.paste(self.__figToImg(self.line1Figures[3]), (4600, 50), self.__figToImg(self.line1Figures[3]))
        # rectangle 1
        draw = ImageDraw.Draw(self.backGround)
        draw.rectangle((1500, 450, 2200, 1050), fill='#03287f', outline=None, width=10)
        draw.text((1700, 500), "Thị phần", (255, 255, 255), font=tiny_font, stroke_width=2)
        draw.text((1550, 690), "0.252%", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theCrown, (1850, 630), self.theCrown.convert("RGBA"))
        draw.text((2080, 690), "1", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theGreenTriangle, (1650, 850), self.theGreenTriangle.convert("RGBA"))
        draw.text((1800, 875), "15%", (255, 255, 255), font=tiny_font, stroke_width=2, color='#00ff00')
        # rectangle 2
        draw.rectangle((1500, 1150, 2200, 1750), fill='#03287f', outline=None, width=10)
        draw.text((1600, 1200), "Phí giao dịch", (255, 255, 255), font=tiny_font, stroke_width=2)
        draw.text((1650, 1390), "125", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theCrown, (1850, 1330), self.theCrown.convert("RGBA"))
        draw.text((2080, 1390), "1", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theGreenTriangle, (1650, 1550), self.theGreenTriangle.convert("RGBA"))
        draw.text((1800, 1550), "20%", (255, 255, 255), font=tiny_font, stroke_width=2, color='#00ff00')
        # rectangle 3
        draw.rectangle((2300, 450, 3000, 1050), fill='#03287f', outline=None, width=10)
        draw.text((2350, 500), "Doanh thu lãi vay", (255, 255, 255), font=tiny_font, stroke_width=2)
        draw.text((2450, 690), "250", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theStar, (2650, 650), self.theStar.convert("RGBA"))
        draw.text((2850, 690), "3", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theRedTriangle, (2400, 850), self.theRedTriangle.convert("RGBA"))
        draw.text((2550, 875), "15%", (255, 255, 255), font=tiny_font, stroke_width=2, color='#00ff00')
        # rectangle 4
        draw.rectangle((2300, 1150, 3000, 1750), fill='#03287f', outline=None, width=10)
        draw.text((2400, 1200), "Tài khoản mới", (255, 255, 255), font=tiny_font, stroke_width=2)
        draw.text((2450, 1390), "5", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theStar, (2650, 1350), self.theStar.convert("RGBA"))
        draw.text((2850, 1390), "5", (255, 255, 255), font=tiny_font, stroke_width=2)
        self.backGround.paste(self.theRedTriangle, (2400, 1550), self.theRedTriangle.convert("RGBA"))
        draw.text((2550, 1550), "50%", (255, 255, 255), font=tiny_font, stroke_width=2, color='#00ff00')
        # text
        draw.text((2400, 100), "BÁO CÁO THÀNH TÍCH CHI NHÁNH \n Từ đầu tháng đến ngày 09/02/2023", (255, 255, 255),
                  font=big_font, stroke_width=2)
        draw.text((3500, 500), "Biến động phí giao dịch", (255, 255, 255), tiny_font)
        draw.text((5200, 500), "Biến động doanh thu lãi vay", (255, 255, 255), tiny_font)
        ''' line 2 '''
        self.backGround.paste(self.__figToImg(self.line2Figures[0]), (50, 1800), self.__figToImg(self.line2Figures[0]))
        self.backGround.paste(self.__figToImg(self.line2Figures[1]), (1500, 1800), self.__figToImg(self.line2Figures[1]))
        self.backGround.paste(self.__figToImg(self.line2Figures[2]), (2500, 1800), self.__figToImg(self.line2Figures[2]))
        self.backGround.paste(self.__figToImg(self.line2Figures[3]), (3200, 1800), self.__figToImg(self.line2Figures[3]))
        self.backGround.paste(self.__figToImg(self.line2Figures[4]), (4500, 1800), self.__figToImg(self.line2Figures[4]))
        self.backGround.paste(self.__figToImg(self.line2Figures[5]), (5500, 1800), self.__figToImg(self.line2Figures[5]))
        draw.text((550, 1700), "Thị phần", (0, 128, 255), tiny_font, stroke_width=2)
        draw.text((3600, 1700), "Phí giao dịch", (0, 128, 255), tiny_font, stroke_width=2)
        draw.text((300, 1800), "Đóng góp vào PHS 2023 ", (255, 255, 255), tiny_font)
        draw.text((1400, 1800), "Thực tế và chỉ tiêu 2023 ", (255, 255, 255), tiny_font)
        draw.text((2400, 1800), "Thực tế và chỉ tiêu 2022 ", (255, 255, 255), tiny_font)
        draw.text((3400, 1800), "Đóng góp vào PHS 2023 ", (255, 255, 255), tiny_font)
        draw.text((4400, 1800), "Thực tế và chỉ tiêu 2023 ", (255, 255, 255), tiny_font)
        draw.text((5400, 1800), "Thực tế và chỉ tiêu 2022 ", (255, 255, 255), tiny_font)
        ''' line 3 '''
        self.backGround.paste(self.__figToImg(self.line3Figures[0]), (50, 3300), self.__figToImg(self.line3Figures[0]))
        self.backGround.paste(self.__figToImg(self.line3Figures[1]), (1500, 3300), self.__figToImg(self.line3Figures[1]))
        self.backGround.paste(self.__figToImg(self.line3Figures[2]), (2500, 3300), self.__figToImg(self.line3Figures[2]))
        self.backGround.paste(self.__figToImg(self.line3Figures[3]), (3200, 3300), self.__figToImg(self.line3Figures[3]))
        self.backGround.paste(self.__figToImg(self.line3Figures[4]), (4500, 3300), self.__figToImg(self.line3Figures[4]))
        self.backGround.paste(self.__figToImg(self.line3Figures[5]), (5500, 3300), self.__figToImg(self.line3Figures[5]))
        draw.text((550, 3200), "Doanh thu lãi vay", (0, 128, 255), tiny_font, stroke_width=2)
        draw.text((3600, 3200), "Tài khoản mới", (0, 128, 255), tiny_font, stroke_width=2)
        draw.text((300, 3300), "Đóng góp vào PHS 2023 ", (255, 255, 255), tiny_font)
        draw.text((1400, 3300), "Thực tế và chỉ tiêu 2023 ", (255, 255, 255), tiny_font)
        draw.text((2400, 3300), "Thực tế và chỉ tiêu 2022 ", (255, 255, 255), tiny_font)
        draw.text((3400, 3300), "Đóng góp vào PHS 2023 ", (255, 255, 255), tiny_font)
        draw.text((4400, 3300), "Thực tế và chỉ tiêu 2023 ", (255, 255, 255), tiny_font)
        draw.text((5400, 3300), "Thực tế và chỉ tiêu 2022 ", (255, 255, 255), tiny_font)
        ''' line 4 '''
        draw.text((550, 4800), "03 nhân viên xuất sắc nhất của chi nhánh", (0, 128, 255), tiny_font, stroke_width=2)
        self.backGround.paste(self.__figToImg(self.line4Figures[0]), (0, 5000), self.__figToImg(self.line4Figures[0]))
        self.backGround.paste(self.__figToImg(self.line4Figures[1]), (2000, 5000), self.__figToImg(self.line4Figures[1]))
        self.backGround.paste(self.__figToImg(self.line4Figures[2]), (4000, 5000), self.__figToImg(self.line4Figures[2]))
        ''' line 5 '''
        draw.text((550, 6100), "So sánh 12 tháng năm 2023", (0, 128, 255), tiny_font, stroke_width=2)
        draw.text((200, 6300), "Phí giao dịch", (255, 255, 255), tiny_font)
        draw.text((2400, 6300), "Doanh thu lãi vay", (255, 255, 255), tiny_font)
        draw.text((4500, 6300), "Tài khoản mới", (255, 255, 255), tiny_font)
        self.backGround.paste(self.__figToImg(self.line5Figures[0]), (0, 6300), self.__figToImg(self.line5Figures[0]))
        self.backGround.paste(self.__figToImg(self.line5Figures[1]), (2200, 6300), self.__figToImg(self.line5Figures[1]))
        self.backGround.paste(self.__figToImg(self.line5Figures[2]), (4400, 6300), self.__figToImg(self.line5Figures[2]))
        self.backGround.save('new_img.png')


# class vẽ biểu đồ gồm 4 piechart chòng lên nhau
class test(Chart):
    def __init__(self):
        super().__init__()

    def draw(self):
        # line 1
        self.data = pd.read_excel('curved_barchart_matplotlib_test.xlsx')
        fig1 = self.drawCurvedBar()
        self.data = pd.read_excel('line_matplotlib_test.xlsx')
        fig2 = self.drawLineChart()
        fig3 = self.drawLineChart()
        fig4 = self.drawMonthProgress('2023-02-09')
        line1 = [fig1, fig2, fig3, fig4]
        # line 2
        self.data = 35
        fig1 = self.drawPieChart()
        fig4 = self.drawPieChart()
        self.data = [35, 55]
        fig2 = self.drawSimpleBarChart()
        fig3 = self.drawSimpleBarChart()
        fig5 = self.drawSimpleBarChart()
        fig6 = self.drawSimpleBarChart()
        line2 = [fig1, fig2, fig3, fig4, fig5, fig6]
        # line 3
        self.data = 35
        fig1 = self.drawPieChart()
        fig4 = self.drawPieChart()
        self.data = [49, 68]
        fig2 = self.drawSimpleBarChart()
        fig3 = self.drawSimpleBarChart()
        self.data = [15, 25]
        fig5 = self.drawSimpleBarChart()
        fig6 = self.drawSimpleBarChart()
        line3 = [fig1, fig2, fig3, fig4, fig5, fig6]
        # line 4
        self.data = [40000, 50000, 70000, 54000]
        fig1 = self.drawDonutChart()
        fig2 = self.drawDonutChart()
        fig3 = self.drawDonutChart()
        line4 = [fig1, fig2, fig3]
        # line 5
        self.data = pd.read_excel('matplotlib_test.xlsx')
        fig1 = self.drawBarChart()
        fig2 = self.drawBarChart()
        fig3 = self.drawBarChart()
        line5 = [fig1, fig2, fig3]
        writer = ImageWriter(line1, line2, line3, line4, line5)
        writer.writeImage()


