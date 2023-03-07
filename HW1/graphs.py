import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import numpy as np

def showTransmissionTimeByMessagePlot(columnUsed, colors):
    fig, ax = plt.subplots()
    for mechanism, group in data.groupby(columnUsed):
        ax.scatter(group['Buffer Size'], group['Transmission Time'], c=colors[mechanism], label=mechanism)
    # Set labels and title
    ax.set_xlabel('Buffer Size')
    ax.set_ylabel('Transmission Time')
    ax.set_title('Transmission Time by Buffer Size')
    # Add legend
    ax.legend()
    # Show plot
    plt.savefig('Transmission Time by Buffer Size_' + columnUsed)
    plt.show()


if __name__ == '__main__':
    # Load data from the CSV file
    data = pd.read_csv("test_results.csv")

    data = data[(np.abs(stats.zscore(data['Transmission Time'])) < 2)]
    # Create a bar chart of transmission time by mechanism used
    plt.bar(data['Mechanism Used'], data['Transmission Time'])
    plt.title('Transmission Time by Mechanism Used')
    plt.xlabel('Mechanism Used')
    plt.ylabel('Transmission Time (seconds)')
    plt.savefig('Transmission Time by Mechanism Used')
    plt.show()


    # Create a scatter plot of Transmission Time by Buffer Size, coloring the points differently based on the Mechanism Used
    colors = {'streaming': 'blue', 'stop-and-wait': 'red'}
    columnUsed = 'Mechanism Used'
    showTransmissionTimeByMessagePlot(columnUsed, colors)

    # Create a scatter plot of Transmission Time by Buffer Size, coloring the points differently based on the Mechanism Used
    colors = {'UDP': 'blue', 'TCP': 'red'}
    columnUsed = 'Protocol'
    showTransmissionTimeByMessagePlot(columnUsed, colors)

    # Create a line chart of number of bytes sent by protocol used
    tcp_data = data[data['Protocol'] == 'TCP']
    udp_data = data[data['Protocol'] == 'UDP']
    plt.plot(tcp_data['Buffer Size'], tcp_data['Number of Sent Bytes'], label='TCP')
    plt.plot(udp_data['Buffer Size'], udp_data['Number of Sent Bytes'], label='UDP')
    plt.title('Number of Bytes Sent by Protocol Used')
    plt.xlabel('Buffer Size (bytes)')
    plt.ylabel('Number of Bytes Sent')
    plt.legend()
    plt.savefig('Number of Bytes Sent by Protocol Used')
    plt.show()
