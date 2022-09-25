const category = require('express').Router();
const csv = require('csvtojson')
const iconv = require('iconv-lite');

category.get('/', (req, res) => {
  var type = req.query.type;
  var data = []
  var top5 = []
  var playPercent = [0, 0, 0, 0]
  var year = [0, 0, 0, 0, 0, 0, 0]
  var comments = {
    long: [0, 0, 0, 0],
    short: [0, 0, 0, 0]
  }
  const converter = csv()
    .fromFile(`./public/${type}.csv`, { encoding: 'binary' })
    .then((json) => {
      var buf = Buffer.from(JSON.stringify(json), 'binary');
      var str = iconv.decode(buf, 'utf-8');
      str = JSON.parse(JSON.stringify(str))
      data = eval(str)
      for (let i = 0; i < 5; i++) top5.push(data[i])
      top5.forEach((item, index) => {
        filterData(item, index, 'play', 'filterPlay')
        filterData(item, index, 'label', 'filterLabel')
      })
      data.forEach((item, index) => {
        filterData(item, index, 'play', type = 0)
        var date = parseInt(item['date'].substring(0, 4))
        if (date) typeData(date, type = 1)
        var long = parseInt(item.longComments) ? parseInt(item.longComments) : 0
        var short = parseInt(item.shortComments) ? parseInt(item.shortComments) : 0
        typeData([long, short], type = 2)
      })
      res.json({
        data: {
          top5,
          playPercent,
          year,
          comments
        },
        message: '处理成功',
        status: 200
      });
    })

  function filterData(obj, index, name, filterName = null, type = null) {
    var numStr = obj[name]
    if (numStr.indexOf('亿') || numStr.indexOf('万')) {
      danwei = numStr[numStr.length - 1]
      numStr = numStr.substring(0, numStr.length - 1)
      if (numStr.indexOf('.') == -1) numStr += '0'
      if (danwei == '亿') numStr = parseInt(numStr.replace('.', '') + "0000000")
      if (danwei == '万') numStr = parseInt(numStr.replace('.', '') + "000")

      if (filterName) top5[index][filterName] = numStr;
      else if (!type) typeData(numStr, type)
    }
  }

  function typeData(numStr, type) {
    var set = []
    if (!type) {
      set = [0, 100000, 1000000, 10000000, Number.MAX_VALUE]
      numStr = parseInt(numStr)
      for (let i = 0; i < set.length - 1; i++) {
        if (numStr >= set[i] && numStr < set[i + 1]) playPercent[i]++
      }
    } else if (type == 1) {
      set = [0, 2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023]
      for (let i = 0; i < set.length - 1; i++) {
        // 0-2000(含2000)
        if (numStr > set[i] && numStr <= set[i + 1]) year[i]++
      }
    } else {
      let long = numStr[0];
      let short = numStr[1];
      if (long >= 0 && long < 100) comments.long[0]++
      else if (long >= 100 && long < 500) comments.long[1]++
      else if (long >= 500 && long < 1000) comments.long[2]++
      else comments.long[3]++

      if (short >= 0 && short < 100) comments.short[0]++
      else if (short >= 100 && short < 500) comments.short[1]++
      else if (short >= 500 && short < 1000) comments.short[2]++
      else comments.short[3]++
    }
  }
});

module.exports = category;