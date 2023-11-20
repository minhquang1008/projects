import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Wedge, Rectangle


class bar_chart:

    def __init__(self, targets, performance):
        self.targets = targets
        self.month = ('JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC', ' JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN')
        self.performance = performance
        # tỉnh tỷ lệ thực tế/ kế hoạch để tô màu
        self.ratio = self.performance/self.targets

    # hàm dùng để add label vào các bar
    @staticmethod
    def __addLabels(x, y):
        for i in range(len(x)):
            plt.text(i, y[i]//10, "{:,}".format(y[i]), ha='center', rotation=90, fontsize=14)

    def drawBarChart(self):
        # data
        ind = np.arange(len(self.month))
        # chỉnh màu theo ratio
        colors = ["#FF4354" if i < 0.9 else "#FFBC01" if 1 > i >= 0.9 else '#00A0B6' for i in self.ratio]
        # size của biểu đồ
        fig=plt.figure(figsize=(14, 7))
        # subplot
        ax = fig.add_subplot()
        # ẩn các cột trái phải và bên trên
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # ẩn dấu gạch - cột x cột y
        plt.tick_params(axis='both',
                        left=False,
                        top=False,
                        right=False,
                        bottom=False,
                        labelleft=True,
                        labeltop=False,
                        labelright=False,
                        labelbottom=True)
        # tạo legend
        color_map = {'Actual>=100% of Target': '#00A0B6',
                     'Actual<100% and >=90% of Target': '#FFBC01',
                     'Actual <90% of Target': '#FF4354', 'Target': 'black'}
        labels = list(color_map.keys())
        handles = [plt.Rectangle((0, 0),1, 1, color=color_map[label]) for label in labels]
        plt.legend(handles, labels, frameon=False, ncol=4, loc=9, fontsize=10)
        # vẽ bar chart trong suốt để tạo đường kẻ bên ngoài các cột
        Bars_unfilled = plt.bar(ind, self.targets, align='center',color='white', fill=True, width=0.6,edgecolor='grey',linewidth=0.5)
        # đè bar chart thật lên trên
        Bars = plt.bar(ind, self.performance, align='center',color=colors,width=0.5)
        # chỉnh format số cột y
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
        # chỉnh cỡ chữ cột y
        plt.yticks(fontsize=14)
        # add label vào từng bar
        self.__addLabels(ind, self.performance)
        # add tên các tháng vào cột x
        plt.xticks(ind, self.month, fontsize=14)
        # tên biểu đồ
        plt.title("Actual Sales vs Target")
        # điểm bắt đầu và điểm kết thúc của hlines
        x_start = np.array([plt.getp(item, 'x') for item in Bars])
        x_end = x_start+[plt.getp(item, 'width') for item in Bars]
        x_start_unfilled = np.array([plt.getp(item, 'x') for item in Bars_unfilled])
        x_end_unfilled = x_start+[plt.getp(item, 'width') for item in Bars_unfilled]
        # hline: dòng màu trắng để đè lên unfilled bar chart, dòng màu đen thể hiện limit
        plt.hlines(self.targets, x_start_unfilled, x_end_unfilled, color ='white',edgecolor='white',linewidth=3)
        plt.hlines(self.targets, x_start, x_end, color ='black',edgecolor='black',linewidth=3)


class gauge_chart:
    # input một số trong khoản từ 1 đến 180
    def __init__(self, arrow):
        self.arrow = arrow

    @staticmethod
    def __degreeRange():
        start = np.linspace(0, 180, 181, endpoint=True)[0:-1]
        end = np.linspace(0, 180, 181, endpoint=True)[1::]
        mid_points = start + ((end - start) / 2.)
        return np.c_[start, end], mid_points

    def drawGaugeChart(self):
        # 3 màu chia đều 180 hình wedge
        colors = sum([[s] * n for s, n in zip(['#1F466D', '#2F8EA2', '#8DB0D0'], [60, 60, 60])], [])
        # subplots
        fig, ax = plt.subplots()
        # tìm điểm chính giữa 2 cạnh của 1 hình wedge, ví dụ, giữa 28 độ và 29 độ là 28.5 độ
        ang_range, mid_points = self.__degreeRange()
        # hàm Wedge có chức năng vẽ ra 1 phần hình tròn có dạng như miếng pizza
        patches = []
        # gộp 180 hình wedge lại tạo ra nửa hình tròn
        for ang, c in zip(ang_range, colors):
            patches.append(Wedge((0, 0), 0.4, *ang, facecolor=c, edgecolor=c))
        [ax.add_patch(p) for p in patches]
        # vẽ 1 hình tương tự nhưng bán kính chỉ bẳng 1/2 hình đầu tiên và có màu trắng đè lên hình ban đầu
        for ang, c in zip(ang_range, colors):
            patches.append(Wedge((0, 0), 0.2, *ang, facecolor='w', edgecolor='w'))
        [ax.add_patch(p) for p in patches]
        # set chữ số chú thích vào phần bottom
        r = Rectangle((-0.4, -0.1), 0.8, 0.1, facecolor='w', lw=2)
        ax.add_patch(r)
        ax.text(0, -0.05, str(self.arrow), horizontalalignment='center',
                verticalalignment='bottom', fontsize=22, fontweight='bold')
        ax.text(-0.3, -0.05, '0', horizontalalignment='left',
                verticalalignment='top', fontsize=22, fontweight='bold')
        ax.text(0.35, -0.05, '180', horizontalalignment='right',
                verticalalignment='top', fontsize=22, fontweight='bold')
        # vẽ mũi tên
        ax.axis("equal")
        pos = mid_points[abs(self.arrow- 180)]
        # tính tọa độ xy điểm điểm muốn mũi tên hướng đến, chỉnh kích thước mũi tên
        ax.arrow(0, 0, 0.225 * np.cos(np.radians(pos)), 0.225 * np.sin(np.radians(pos)),
                 width=0.01, head_width=0.01, head_length=0.18, fc='#474B6E', ec='#474B6E')
        # bỏ border line
        ax.set_frame_on(False)
        ax.axes.set_xticks([])
        ax.axes.set_yticks([])


class curved_bar:

    def __init__(self, criteria, complete):
        self.criteria = criteria
        self.complete = complete
        # bán kinh hình tròn bên ngoài
        self.r = 1.5
        # bán kinh hình tròn bên trong
        self.r_inner = 0.4
        self.colors = ['#40AEA3', '#3E4A57', '#6E8297', '#7F7F7F']

    def drawCurvedBar(self):
        # số lượng tiêu chí input vào biểu đồ
        n = len(self.complete)
        # tỷ lệ hoàn thành lớn nhất
        p = lambda i: 100 if i>100 else i
        [p(i) for i in self.complete]
        percent_circle = max(self.complete) / 100
        # tính chiều rộng mỗi ring
        w = (self.r - self.r_inner) / n
        # tạo figure, axis
        fig, ax = plt.subplots(figsize=(7, 7))
        # vẽ biểu đồ
        for i in range(n):
            radius = self.r - i * w
            # hàm ẩn danh điều chỉnh lại vị trí các label vì hình piechart càng lớn thì tỷ lệ pctdistance cũng khác nhau
            # vd: 20/10 > 10/10
            p = lambda p: 0.91 if i == 0 else 0.89 if i == 1 else 0.86 if i == 2 else 0.8
            # pie chart
            ax.pie([(self.complete[i] / max(self.complete) * percent_circle),
                    (1 - (self.complete[i] / max(self.complete) * percent_circle))],
                   radius=radius, startangle=90,
                   counterclock=False,
                   colors=[self.colors[i], 'white'], labeldistance=None,
                   wedgeprops={'width': w, 'edgecolor': 'white', 'linewidth': 8.5, 'alpha': 1},
                   autopct='%.f%%', textprops={'color': 'w', 'weight': 'bold', 'fontsize': 12.5}, pctdistance=p(i))
            ax.text(0, radius - w / 2, f'{self.criteria[i]}', ha='right', va='center', fontsize=12, weight='bold')
        plt.tight_layout()
        plt.show()


class pie_chart:

    def __init__(self, data):
        self.data = data

    def drawPieChart(self):
        myexplode = [0.1, 0]
        color = ['#5b9bd5', '#ed7d31']
        label = ['{}%'.format(self.data[0]), '']
        plt.pie(self.data,
                explode=myexplode,
                colors=color,
                labels=label,
                labeldistance=0.5,
                textprops={'fontsize': 12.5})
        plt.show()


class donut_chart:

    def __init__(self, contribution):
        self.broker = ['Broker A', 'Broker B', 'Broker C', '_nolegend_']
        self.contribution = contribution
        self.colors = ['#f06544', '#edbf41', '#62b890', '#3087ae']

    def drawDonutChart(self):
        # data mẫu
        # [40000, 50000, 70000, 54000]
        # vẽ Pie Chart
        plt.pie(self.contribution, colors=self.colors, autopct='%1.0f%%')
        # vẽ hình tròn màu trắng
        centre_circle = plt.Circle((0, 0), 0.35, fc='white')
        # đè hình tròn màu trắng lên chính giữa pie chart
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        # add title
        plt.title('Highest new accounts')
        # add legend
        plt.legend(self.broker, bbox_to_anchor=(1, 1))
        # show
        plt.show()


class line_chart:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def drawLineChart(self):
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        plt.ylabel("Total Units")
        ax.grid(axis='y')
        ax.set_xticks(self.x)
        plt.xticks(rotation=45)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        reformat = mdates.DateFormatter('%b-%y')
        ax.xaxis.set_major_formatter(reformat)
        plt.tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=True, labeltop=False,
                        labelright=False, labelbottom=True)
        plt.plot(self.x, self.y, color='#62b2ac')
        plt.show()
