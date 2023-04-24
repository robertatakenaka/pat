import * as echarts from 'echarts';

var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom);
var option;

const labelRight = {
  position: 'right'
};
option = {
  title: {
    text: 'Bar Chart with Negative Value'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    top: 80,
    bottom: 30
  },
  xAxis: {
    type: 'value',
    position: 'top',
    splitLine: {
      lineStyle: {
        type: 'dashed'
      }
    }
  },
  yAxis: {
    type: 'category',
    axisLine: { show: false },
    axisLabel: { show: false },
    axisTick: { show: false },
    splitLine: { show: false },
    data: {{ slices_labels }}
  },
  series: [
    {
      name: 'Cost',
      type: 'bar',
      stack: 'Total',
      label: {
        show: true,
        formatter: '{b}'
      },
      data: {{ slices_data }}
    }
  ]
};

option && myChart.setOption(option);
