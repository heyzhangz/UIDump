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

#### 半自动Dump
在该模式下，需要人为手动触发相关场景，按"home"键停止Dump。
```
py ./UIDump.py -p com.tencent.mm
```

#### 全自动Dump
**需要指定 -m 参数开启改模式**
在该模式下，采用monkey代替手动触发相关场景。
因为monkey需要白名单来指定可触发的package范围，如需补充可扩展`./monkey_pkg_whitelist.txt`文件

```
py ./UIDump.py -p com.tencent.mm -m 1800000
```

#### 批量全自动Dump
**TODO**
目前流程比较简单，就是读取app目录，逐个调用全自动的UIDump，具体运行参数可以在脚本中直接修改

```
py ./Multi-UIDump.py
```

