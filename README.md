### UIDump

#### 使用
```
py UIDump.py -p <app-package-name> [-t <dump-interval>] [-r <replay-script>]

	-p --package <app-package-name> 用来录制或者重放的app包名
	-t --interval <dump-interval> dump UI 的时间间隔，默认是1s
	-r --replay <replay-script> 重放模式，需要提供重放脚本；不使用该参数为记录模式

```

#### 记录操作
```
py ./UIDump.py -p com.tencent.mm
```
记录操作时，会自动打开指定包名的app，随后会记录人为操作顺序。若要终止记录，退出APP即可。
终止记录后会进行一次操作重放，在重放过程中会dump UI信息到./output/record目录，其中：
recordevents.txt	为getevent的log
replayscript.txt	 为重放脚本

#### 重放操作
```
py ./UIDump.py -p com.tencent.mm -r ./output/record/com.tencent.mm_202004091643/replayscript.txt
```
重放操作需要通过 -r 参数指定重放脚本。
在重放过程中会dump UI信息到./output/replay目录。