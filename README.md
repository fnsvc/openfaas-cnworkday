# openfaas-cnworkday

查询指定日期在中国大陆是否是工作日，以及一些额外信息，包括：

- 是否是工作日
- 是否是节假日
- 是否是周末
- （可选）节假日描述

## API 使用方法

使用 HTTP GET 访问 <https://f.mynook.info/function/cn-workday>，携带以下参数：

- `date`: 可选，形如 `2013-12-25` 的日期字符串。如果不传递参数则使用当前日期。

## API 响应

响应为 JSON 格式。正常响应的内容如下：

```json
{
    "code": 0,
    "data": {
        "date": "2019-04-27",
        "is_weekend": true,
        "is_holiday": false,
        "is_workday": false,
        "description": ""
    }
}
```

如果调用出现错误，JSON 响应体中 `code` 字段不为 0，且会带有 `msg` 字段说明详细错误信息。

## API code

- `0`: 没有错误
- `1`: 日期格式错误
- `2`: 没有指定年份的数据

## 数据收录

数据来自国务院一年一度发布的次年节假日安排通知。目前收录的年份有：

- 2017
- 2018
- 2019

# License

See <LICENSE> file.

