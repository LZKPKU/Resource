

# git学习笔记

## git安装

略

## 创建版本库

```
mkdir  name

cd  name

git init
```



就可以把name变成一个空的仓库。用

`ls -ah`

可以查看其中的内容

## 添加文件到版本库

所有的版本控制系统，其实只能跟踪文本文件的改动，例如TXT文件。二进制文件无法跟踪，所以要以纯文本方式编写文件，不能用MS word，也不能用记事本。

可以用Notepad++的UTF-8 without BOM.

```
git add name
git commit -m “comment”
```



提交文件需要add、commit两个步骤，commit一次可以提交很多文件，这些文件可以是多次add上的不同的文件。



## 掌握仓库当前的状态

`git status`

`git diff`

diff可以显示不同，格式是Unix通用的diff格式。

## 版本回退

`git log [--pretty=oneline]`

可以查看修改的记录和注释（[加上可以让消息更简洁]）。每提交一个新版本，Git就会自动把它们串成一条时间线。id是SHA1计算出来的相当大的数字。

```
git reset --hard HEAD^
git reset --hard HEAD~1
git reset --hard 19238928398192891
```

回退到上一个版本，三条语句等价，^看数量，1看数字，版本号就是版本号。版本号不需要打全。

当然也可以回到未来，前提是，你的命令行里还留着未来版本号，否则Git会把它丢弃，这样就找不回来了。

但这样也能找回来——



`git reflog`

记录你的每一次命令，这样就能看到未来文件的版本号了。

## 工作区和暂存区

第一步是用`git add`把文件添加进去，实际上就是把文件修改添加到暂存区(stage)；

第二步是用`git commit`提交更改，实际上就是把暂存区的所有内容提交到当前分支。

## 管理修改

Git的优秀之处在于它跟踪管理的是修改，不是文件。

## 撤销修改

撤销还未add的修改。

`git checkout -- file`可以让文件回到最近一次`git commit`或者`git add`操作时的状态。

已经add进去了。

`git reset HAED file`可以让文件复原。

一旦提交，就要求助于版本回退的内容。前提是还没有把自己的本地版本库推送的远程。

## 删除文件

`git checkout`其实是用版本库里的版本替换工作区的版本，无论工作区是修改还是删除，都可以“一键还原”。

首先先在本地删除文件，Git发现不一致会提醒你。`git rm`是确实想删。如果是删错了就用`git checkout`

## 远程仓库

GitHub是给Git仓库提供托管服务的，所以只要注册一个GitHub账号，就可以免费获取Git远程仓库。

需要设置SSH KEY，每台电脑一个。在GitHub上免费托管的仓库是所有人都可以看见的。

要关联一个远程库，使用命令

`git remote add origin https://github.com/LZKPKU/repo-name.git`

或者

`git remote add origin git@github.com:LZKPKU/repo-name.git`

这是因为git支持多种协议，git：//默认使用ssh，但也可以使用https等其他协议。通过ssh支持的原生git协议速度最快。

把本地库内容推送到远程，用`git push`命令，实际上是把当前分支master推送到远程。

以后，只要本地做了提交，就可以通过命令`git push origin master`把本地master分支的最新修改推送到GitHub。

## 从远程库克隆

假设我们从零开发，那么最好的方式是先创建远程库，然后从远程库克隆。

远程库准备好了以后，用命令`git clone`克隆一个本地库。



如果有多个人协作开发，那么每个人各自从远程克隆一份就可以了。

要克隆一个仓库，首先必须知道仓库的地址，然后使用`git clone`命令克隆。

## 创建分支

`git branch dev`

`git chekout dev`

第一条语句创建分支，第二条切换分支。

用一句实现就是`git checkout -b dev`

使用`git branch`可以看当前仓库的分支情况。

用`git checkout master`可以转回master分支。

之后用`git merge dev`可以把dev分支的工作成果合并到master分支上。

## 团队合作策略

master上一般不干活，仅仅用来发布新版本，dev分支是不稳定的，每个人都有自己的分支，在自己的分支上干活，干完之后往dev分支上合并就可以了。

如果要修复bug，一般是进到要修改的分支里面创建一个临时分支，在临时分支里面改完后，合并到原分支。原来进行的工作可以用`git stash`储存起来，之后用`git stash pop`恢复

如果要丢弃一个没有被合并过的分支，可以通过`git branch -D name `强行删除。

## 推送分支

用 `git remote-v`查看远程仓库的详细信息，远程仓库的默认名称是origin.

上面显示了可以抓取和推送的origin的地址。如果没有推送权限，就看不到push的地址。

`git push origin master`推送master分支到远程仓库

`git push origin dev`推送dev分支到远程仓库

一般来讲master是主分支，要时刻与远程同步；dev是开发分支，团队所有成员需要在上面工作，所以也需要与远程同步。总之，在Git中，分支完全可以在本地藏着玩，是否推送，看心情而定。

## 抓取分支

当我们从远程库clone时，默认只能看到master分支，如果要在dev上开发，就必须创建远程origin的dev分支到本地，用`git checkout -b dev origin/dev`

指定本地dev分支与远程origin/dev分支的链接

`git branch --set-upstream dev origin/dev`

多人协作的工作模式：

1. 可以用`git push origin branch-name`推送自己的修改
2. 如果推送失败，说明远程分支比你的新，需要用`git pull`试图合并
3. 合并并解决掉可能出现的冲突后，再用`git push origin branch-name`提交。

PS：如果`git pull`提示“no tracking information”，则说明本地分支和远程分支的链接关系没有创建，用命令`git branch --set-upstream branch-name origin/branch-name`

## 创建标签

标签只是因为版本号太长不好记，就用了tag，类比IP地址和域名的关系。

创建标签时，切换到需要添加标签的分支，然后输入`git tag name`就行了。

默认是对最新提交的一次commit打，如果想对之前提交的打标签，需要用

`git log --pretty=oneline --abbrev-commit`来查看所有的commit记录，找到commit id，然后用`git tag name id`来打标签。

用`git show tagname`来查看某一个标签的详细信息。

-a 制定标签名 -m指定说明文字

标签可以删除，用`git tag -d nameb`

标签推送到远程用`git push origin tagname`

推送全部标签用`git push origin --tags`

## 使用GitHub

把想改的库fork到自己这里来，然后clone到本地主机。改好之后pull request，别人决定是否接受。

## 忽略特殊文件

某些文件需要放到工作目录里，但是又不能提交。

可以在工作区的根目录底下创建一个特殊的`.gitignore`文件，然后把要忽略的文件名填进去。

之后需要把这个文件提交上去，如果想提交在这个文件中被忽略的文件，用-f强制。

还可以用`git check-ignore -v filename`来查看某一文件到底被.gitignore中的哪句给忽略了，可以有针对性地修改。

## 配置别名

用`git config --global alias.st status `来把status的别名设置为st

--global参数是全局参数，它的配置对于电脑上的所有的git仓库都有用。



