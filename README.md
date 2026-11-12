# 关键筹码置顶 PinnedRelicsMod 1.2.0

《吉星派对》（Astral Party）CesiumLoader 独立模组。
玩家持有名单内的筹码时，在左侧对应玩家星币下方横排显示图片。
保留原有大小和位置配置，默认图标大小 30、间距 3，不额外添加背景或描边。

## 1.2.0：直接使用游戏内置图片

- 使用游戏自己的 `RelicInfoConfigure.Icon` 获取图案地址，由 `UI.TextureLoader` 和 `TextureManager` 加载。
- 品质底圈使用游戏公共 UI 的 `UICom_Relic_Quality`，按游戏配置设置蓝、紫、金等品质。
- 与游戏玩家详情界面的筹码使用同一套资源和加载路径，不再读取或附带 Wiki PNG，也不需要 `assets` 文件夹。
- 纹理由游戏管理器缓存。移除图标时通过原生 loader 归还引用，不手工销毁游戏共用纹理。
- 保留中文名配置，当前名称目录包含 90 种筹码；原来缺少 Wiki 图片的“时间怀表(破碎)”也可配置。

使用原生资源可保持与游戏一致的素材和加载方式，避免外部 PNG 的额外解码。小尺寸下的可读性仍受图标大小、界面缩放和游戏原始素材影响，不能保证仅更换来源就一定更清晰。

## 添加、删除置顶筹码

在启动器“关键筹码置顶”的配置页修改 **`PinnedRelicNames`**，也可编辑模组目录下的 `config.json`。
默认保留原来的六种。在末尾增加“星币锤”的示例：

```json
"PinnedRelicNames": "肾上腺素-高效,磨刀石,友情徽章,安全气囊,紫色飞星,金色飞星,星币锤"
```

这是一项配置字段的示例，不要用这一行覆盖整份 JSON。
启动器输入框中只填写名字列表，不必输入字段名或引号。

- 支持中文或英文逗号、顿号、分号、换行和 `|` 分隔。
- 按填写顺序排列；删掉名字即可取消该筹码置顶；空字符串 `""` 清空显示。
- 同种筹码只显示一次，仅在对应玩家持有时显示，不留空格。
- “友情微章”也可识别为游戏内的“友情徽章”。
- 完整名单见随包 [支持的筹码.md](支持的筹码.md)。未知或错误名字会跳过并在日志提示，不影响其他筹码。
- 名称目录直接编入代码，不读取 DLL 内嵌资源，避免 1.1.0 曾遇到的 HybridCLR 接口缺失。
- 保存后由加载器配置热重载生效。若启动器没有触发重载，重新启动游戏即可。

## 显示行为

四名玩家分别显示各自持有状态，旁观时跟随左侧对应玩家栏。
获得或失去筹码后，通常在下一次刷新（0.2 秒）更新。
持有即显示，不按生命值或充能是否满足效果触发条件来隐藏。
仅显示图片，不显示名称、点数、层数或说明，不更改游戏原有筹码排序或任何对局数据。

每行空间不足时等比缩小，保持横排。大量筹码同时置顶会使图标变小，建议只填写需要关注的筹码。
图标不接收鼠标输入，不影响头像按钮操作，HUD 隐藏时随之隐藏。

## 安装与更新

在支持 CesiumLoader 的启动器导入 `PinnedRelicsMod-1.2.0.zip`，启用“关键筹码置顶”，重新启动游戏。
手动安装时，先退出游戏，将包中的 `PinnedRelicsMod` 文件夹放入 `AstralParty_ModLoader/mods/`：

```text
AstralParty_ModLoader/
  mods/
    PinnedRelicsMod/
      PinnedRelicsMod.dll
      PinnedRelicsMod.json
      PinnedRelicsMod.pdb
      config.json
      README.md
      支持的筹码.md
      NOTICE.md
      LICENSE
```

已有配置可以保留；中文名名单、大小和偏移均兼容。旧版 `assets` 图片不再使用，可退出游戏后移走。
不要形成重复嵌套的 `PinnedRelicsMod/PinnedRelicsMod/`。
不依赖 BattleCardPointsMod、CombatOddsMod 或 SpeedHackMod。
退出游戏后移除本模组目录即可卸载。

## 其他设置

| 字段 | 默认值 | 作用 |
| --- | --- | --- |
| `Enabled` | `true` | 显示总开关 |
| `PinnedRelicNames` | 原来的六个中文名 | 自定义名单与顺序 |
| `IconSize` | `30` | 图标边长，范围 16～64；空间不足时自动缩小 |
| `IconGap` | `3` | 图标间距，范围 0～20 |
| `OffsetX` | `0` | 相对星币数字左边缘的水平偏移，正数向右，范围 -300～300 |
| `OffsetY` | `3` | 相对星币数字下边缘的垂直偏移，正数向下，范围 -100～200 |

位置和尺寸使用游戏 UI 局部坐标单位，随玩家栏一起移动、缩放，对四名玩家统一生效。

## 性能与生命周期

每 0.2 秒检查玩家持有列表，只在需要时创建图标。图案 URL 每个图标设置一次，由游戏异步加载和缓存；不每帧读磁盘、解码 PNG 或重复发起资源请求。
修改名单或切换场景时移除旧 UI。卸载时清理本模组创建的组件，使用游戏原生纹理引用释放方式。

## 构建与验证

本次使用 CesiumLoader 3.7.0 SDK 编译。清单最低 API 声明为 2.8.6，未验证所有旧加载器。
自行准备 .NET SDK、CesiumLoader SDK 和游戏引用程序集：

```powershell
dotnet build src/PinnedRelicsMod.csproj -c Release `
  -p:SdkDll="D:/path/to/AstralParty_ModLoader/sdk/CesiumLoader.SDK.dll" `
  -p:GameRefsDir="D:/path/to/extracted_dlls" `
  -p:NuGetAudit=false

dotnet run --project tests/CatalogChecks.csproj -c Release -p:NuGetAudit=false
```

产物在 `src/bin/Release/netstandard2.0/`。
更新名称目录需自行提供提取的 `Relic`、`STRRelic` 配表，运行 `tools/build_game_catalog.py --help` 查看用法。
SDK、游戏程序集、原始配表和游戏图片均不随本包分发。

Release 编译通过，0 警告、0 错误；11 项名称与持有列表检查通过。游戏内的原生图标加载效果需实机核对。

## 来源与许可

模组代码按 AGPL-3.0 分发，详见 LICENSE 和 NOTICE.md。
原生 UI、筹码图片及相关商标属于游戏权利人，本模组只调用已安装游戏的资源。
这是非官方第三方模组，未获游戏开发商或运营团队授权，使用前请自行确认游戏规则。
