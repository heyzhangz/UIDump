### UIDump

#### 使用
```
py UIDump.py -p <app-package-name> [-f <apk-file-path>] [-m <monkey-run-time>] [-o <output-path>] [-d <device-id>]

	-p --package <app-package-name> 用来Dump数据的app包名
	-f --apkfile <apk-file-path> 待安装的apk文件路径，需要和-p指定的app包名一致，支持url。
	-m --monkeytime <monkey-run-time> 设置monkey运行的毫秒数，指定该参数的话为全自动模式，monkey计时结束停止录制；未指定该参数为半自动模式，手动操作，按"home"键停止Dump。
	-o --output <output-path> Dump数据的输出路径，默认输出路径为./output/record
	-d --device <device-id> 指定运行设备，默认adb devices列表里第一个设备

```

#### 半自动单任务Dump
在该模式下，需要人为手动触发相关场景，按"home"键停止Dump，结果保存在`output/record/`目录下<br>
```
py ./UIDump.py -p com.tencent.mm
```

#### 全自动单任务Dump
**需要指定 -m 参数开启改模式**<br>
在该模式下，采用monkey代替手动触发相关场景，结果保存在`output/record/`目录下<br>
因为monkey需要白名单来指定可触发的package范围，如需补充可扩展`./monkey_pkg_whitelist.txt`文件<br>

```
py ./UIDump.py -p com.tencent.mm -m 1800000
```

#### 多任务Dump
**该模式需要指定GlogalConfig.py对应参数**<br>
在该模式下，会利用多设备以及app列表来自动化批量Dump，结果保存在`output/record/`目录下，日志保存在`output/log/`目录下。<br>
`Dispatch-` 开头为分发脚本日志<br>
`UIDump-` 开头为该app的Dump日志<br>
<br>
运行结束在根目录会生成两个文件；<br>
`err_app_list.json` 为本次运行失败的app列表<br>
`remain_app_list.json` 为未运行app列表<br>
<br>
参数列表：<br>
`MONKEY_TIME : monkey运行时间`<br>
`DEVICE_LIST : 可选择设备列表，设为空列表或者None则表示可以使用全部在线设备`<br>
`APP_LIST_PATH : app list 文件路径，注意目前格式和category_top.json格式类似，替换列表文件时注意修改下Muliti-UIDump.py的读取逻辑，稳定后统一格式`<br>

```
py ./Multi-UIDump.py
```


