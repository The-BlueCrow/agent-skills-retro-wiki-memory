---
title: 直连被墙时用 REST API 推送
created: 2026-10-26
updated: 2026-10-26
type: concept
tags: [git, tooling]
sources: 自身实践归纳
---

# 直连被墙时用 REST API 推送

现象：`git push` 连 `github.com:443` 超时，但 `api.github.com` 可达（主站被墙、API 通道活着是常见组合）。

不必干等网络恢复——Git 的对象模型完全可以用 REST API 复刻：

1. 每个文件 → `POST /git/blobs`（base64 内容）拿 blob sha；
2. 组树 → `POST /git/trees`（嵌套结构，path 带 `/` 的条目自动建中间树）；
3. 提交 → `POST /git/commits`，`tree` 指上一步，`parents` 填当前 `GET /git/ref/heads/<分支>` 拿到的 sha；
4. 快进 → `PATCH /git/refs/heads/<分支>` 指到新 commit（更新 ref 不是快进会被拒，所以别造无父 commit）。

细节坑：blob sha 可以本地预计算（`sha1("blob <长度>\0" + 内容)`）用来逐文件比对传输完整性，省去下载回来核对；空仓不能直接造对象（409），先用 contents 接口放一个文件激活仓库。

这条路与 [[self-contained-skills|技能自洽原则]] 是同一个思路：通道是手段不是依赖，产物与传输方式解耦。首次部署可参考 [[first-week-setup|新库第一周怎么用]]。
