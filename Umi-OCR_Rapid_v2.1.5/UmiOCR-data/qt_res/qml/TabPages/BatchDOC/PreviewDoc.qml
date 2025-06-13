// ===========================================
// =============== 文档预览面板 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import DocPreviewConnector 1.0

import "../../Widgets"
import "../../Widgets/IgnoreArea"

ModalLayer {
    id: pRoot
    property var updateInfo // 更新信息函数
    property var configsComp: undefined // 设置组件

    property string previewPath: ""
    property string password: ""
    property bool isEncrypted: false // 已加密
    property bool isAuthenticate: false // 密码正确
    property int previewPage: -1
    property int pageCount: -1
    property int rangeStart: -1
    property int rangeEnd: -1
    property int ignoreRangeStart: 1
    property int ignoreRangeEnd: -1
    property bool previewOCR: false // 是否预览OCR
    property bool ocrRunning: false // 是否预览OCR正在执行

    // 展示文档
    // info: path, page_count, range_start, range_end, is_encrypted, password, is_authenticate
    function show(info) {
        imgViewer.clear()
        visible = true
        previewPath = info.path
        pageCount = info.page_count
        previewPage = info.range_start
        rangeStart = info.range_start
        rangeEnd = info.range_end
        password = info.password
        isEncrypted = info.is_encrypted
        isAuthenticate = info.is_authenticate
        // 读取忽略区域设置
        let initArea = configsComp.getValue("tbpu.ignoreArea")
        if(initArea && initArea.length>0) {
            // 读取设置，反格式化
            let ig1 = []
            for(let i=0,l=initArea.length; i<l; i++) {
                const b = initArea[i]
                ig1.push({
                    "x": b[0][0],
                    "y": b[0][1],
                    "width": b[2][0] - b[0][0],
                    "height": b[2][1] - b[0][1],
                })
            }
            imgViewer.ig1Boxes = ig1
        }
        ignoreRangeStart = configsComp.getValue("tbpu.ignoreRangeStart")
        ignoreRangeEnd = configsComp.getValue("tbpu.ignoreRangeEnd")
        toPreview()
    }

    // 返回上层，更新信息
    onVisibleChanged: {
        if(visible) return
        // 负数转倒数
        if(rangeStart < 0) rangeStart += pageCount + 1
        if(rangeEnd < 0) rangeEnd += pageCount + 1
        // 范围检查
        if(rangeStart < 1) rangeStart = 1
        if(rangeStart > pageCount) rangeStart = pageCount
        if(rangeEnd < rangeStart) rangeEnd = rangeStart
        if(rangeEnd > pageCount) rangeEnd = pageCount
        let pages_ = `${pageCount}` // 如果范围为整本，只显示总页数。否则显示 起始-结束
        if(rangeEnd - rangeStart + 1 < pageCount)
            pages_ = `${rangeStart}-${rangeEnd}`
        if(updateInfo) {
            updateInfo(previewPath, {
                pages: pages_,
                state: isAuthenticate ? "" : qsTr("加密"),
                range_start: rangeStart,
                range_end: rangeEnd,
                password: password,
                is_authenticate: isAuthenticate,
            })
        }
        // 更新忽略区域
        if(imgViewer.ig1Boxes.length > 0) {
            // 格式化，存入设置
            let ig1 = []
            for(let i=0,l=imgViewer.ig1Boxes.length; i<l; i++) {
                const b = imgViewer.ig1Boxes[i]
                const x = Math.round(b.x)
                const y = Math.round(b.y)
                const w = Math.round(b.width)
                const h = Math.round(b.height)
                ig1.push([[x, y], [x+w, y], [x+w, y+h], [x, y+h]])
            }
            configsComp.setValue("tbpu.ignoreArea", ig1)
        }
        else {
            configsComp.setValue("tbpu.ignoreArea", undefined)
        }
        configsComp.setValue("tbpu.ignoreRangeStart", ignoreRangeStart)
        configsComp.setValue("tbpu.ignoreRangeEnd", ignoreRangeEnd)
        imgViewer.clear()
        prevConn.clear() // 清除文档缓存
        previewPath = ""
    }

    // 翻页。to直接翻页，flag加减页。
    function changePage(to, flag=0) {
        if (typeof to === "string") {
            to = parseInt(to, 10)
        }
        if(flag != 0) {
            to = previewPage + flag
        }
        if(previewPage != to && to > 0 && to <= pageCount) {
            previewPage = to
            toPreview()
        }
    }
    Keys.onLeftPressed: changePage(-1, -1)  // 上一页
    Keys.onUpPressed: changePage(-1, -1)
    Keys.onRightPressed: changePage(-1, 1) // 下一页
    Keys.onDownPressed: changePage(-1, 1)

    // 预览一页文档
    function toPreview() {
        if(!previewPath) return
        if(previewPage < 1) previewPage = 1
        if(previewPage > pageCount) previewPage = pageCount
        prevConn.preview(previewPath, previewPage, password)
        if(previewOCR) { // 预览OCR
            ocrRunning = true
            const argd = configsComp.getValueDict()
            argd["tbpu.parser"] = "None" // 去除排版解析
            prevConn.ocr(previewPath, previewPage, password, argd)
        }
    }
    // 预览连接器
    DocPreviewConnector {
        id: prevConn
        // 图片渲染的回调
        onPreviewImg: function(imgID) {
            const title = qsTr("打开文档失败")
            if(imgID === "[Warning] is_encrypted") {
                qmlapp.popup.simple(title, qsTr("请填写正确的密码"))
                isAuthenticate = false
            }
            else if(imgID.startsWith("[Error]")) {
                qmlapp.popup.message(title, imgID, "error")
            }
            else {
                imgViewer.showImgID(imgID)
                if(!isAuthenticate) {
                    qmlapp.popup.simple(qsTr("密码正确"), password)
                    isAuthenticate = true
                }
            }
        }
        // ocr预览的回调
        onPreviewOcr: function(info) {
            let path = info[0], page = info[1], res = info[2]
            if(res.code!=100&&res.code!=101) { // 遇到异常
                qmlapp.popup.message(qsTr("文档预览异常"), res.data, "error")
                return
            }
            if(path != previewPath || page != previewPage) {
                console.warn("文档OCR预览回调不匹配")
                return
            }
            ocrRunning = false
            imgViewer.showTextBoxes(res)
        }
    }

    property string ignoreTips: qsTr("忽略区域说明：\n右键拖拽，绘制矩形区域，包含在区域内的文字框将被忽略。可用于排除水印、页眉页脚。\n范围允许填写负数，表示倒数第x页。如-1表示最后一页，-2表示倒数第2页。\n忽略区域的设置对所有文档生效。")

    contentItem: DoubleRowLayout {
        anchors.fill: parent
        initSplitterX: size_.line * 13
        // 左：控制面板
        leftItem: Panel {
            anchors.fill: parent

            ScrollView {
                anchors.fill: parent
                contentWidth: width // 内容宽度
                clip: true // 溢出隐藏

                Column {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: size_.spacing
                    spacing: size_.smallSpacing
                    // ===== 文件名 =====
                    Text_ {
                        text: previewPath
                        anchors.left: parent.left
                        anchors.right: parent.right
                        wrapMode: TextEdit.WrapAnywhere // 任意换行
                        maximumLineCount: 4 // 限制行数
                        color: theme.subTextColor
                        font.pixelSize: size_.smallText
                    }
                    // ===== 密码 =====
                    Row {
                        visible: isEncrypted && !isAuthenticate // 已加密，未填密码，才显示
                        spacing: size_.spacing
                        height: size_.line + size_.spacing * 2
                        Text_ {
                            color: theme.noColor
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("密码：")
                        }
                        TextField_ {
                            width: size_.line * 6
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            text: password
                            onTextChanged: password = text
                        }
                        IconButton {
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: height
                            icon_: "yes"
                            onClicked: toPreview()
                        }
                    }
                    // ===== 控制项 =====
                    Column {
                        visible: !isEncrypted || isAuthenticate
                        spacing: size_.smallSpacing
                        anchors.left: parent.left
                        anchors.right: parent.right
                        // ===== 页数 =====
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            height: 1
                            color: theme.coverColor4
                        }
                        Row {
                            spacing: size_.line
                            height: size_.line
                            Text_ {
                                text: qsTr("预览页面")
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            CheckButton {
                                anchors.verticalCenter: parent.verticalCenter
                                height: size_.line
                                enabledAnime: true
                                checked: previewOCR
                                textColor_: theme.subTextColor
                                onCheckedChanged: {
                                    if(!previewOCR&&checked) {
                                        previewOCR = true
                                        toPreview()
                                    }
                                    else {
                                        previewOCR = ocrRunning = false
                                    }
                                }
                                text_: "OCR"
                                toolTip: qsTr("预览PDF时，是否预览OCR结果")
                            }
                        }
                        Row {
                            spacing: size_.spacing
                            height: size_.line + size_.smallSpacing * 2
                            Button_ {
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                text_: "<"
                                onClicked: changePage(0, -1)
                            }
                            Button_ {
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                text_: ">"
                                onClicked: changePage(0, 1)
                            }
                            TextField_ {
                                width: size_.line * 3
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                validator: IntValidator{bottom: 1; top: pageCount;}
                                text: previewPage
                                onTextChanged: changePage(text)
                            }
                            Text_ {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "/ "+pageCount
                            }
                        }
                        // ===== OCR范围 =====
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            height: 1
                            color: theme.coverColor4
                        }
                        Text_ {
                            text: qsTr("OCR页数")
                        }
                        Row {
                            height: size_.line + size_.smallSpacing * 2
                            spacing: size_.spacing
                            Text_ {
                                font.pixelSize: size_.smallText
                                anchors.verticalCenter: parent.verticalCenter
                                text: qsTr("范围")
                            }
                            TextField_ {
                                width: size_.line * 3
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                validator: IntValidator{bottom: -pageCount; top: pageCount;}
                                text: rangeStart
                                onTextChanged: {
                                    if(text !== "" && text !== "-") rangeStart = text
                                }
                            }
                            Text_ {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "-"
                            }
                            TextField_ {
                                width: size_.line * 3
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                validator: IntValidator{bottom: -pageCount; top: pageCount;}
                                text: rangeEnd
                                onTextChanged: {
                                    if(text !== "" && text !== "-") rangeEnd = text
                                }
                            }
                        }
                        // ===== 忽略区域 =====
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            height: 1
                            color: theme.coverColor4
                        }
                        Text_ {
                            text: qsTr("忽略区域页数（全局）")
                        }
                        Row {
                            height: size_.line + size_.smallSpacing * 2
                            spacing: size_.spacing
                            Text_ {
                                font.pixelSize: size_.smallText
                                anchors.verticalCenter: parent.verticalCenter
                                text: qsTr("范围")
                            }
                            TextField_ {
                                width: size_.line * 3
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                validator: IntValidator {}
                                text: ignoreRangeStart
                                onTextChanged: {
                                    if(text !== "" && text !== "-") ignoreRangeStart = text
                                }
                            }
                            Text_ {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "-"
                            }
                            TextField_ {
                                width: size_.line * 3
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                validator: IntValidator {}
                                text: ignoreRangeEnd
                                onTextChanged: {
                                    if(text !== "" && text !== "-") ignoreRangeEnd = text
                                }
                            }
                        }
                        Row {
                            spacing: size_.spacing
                            height: size_.smallLine + size_.smallSpacing * 2
                            Button_ {
                                anchors.verticalCenter: parent.verticalCenter
                                height: size_.smallLine + size_.smallSpacing
                                bgColor_: theme.coverColor1
                                text_: qsTr("撤销")
                                onClicked: imgViewer.revokeIg()
                                textSize: size_.smallText
                            }
                            Button_ {
                                anchors.verticalCenter: parent.verticalCenter
                                height: size_.smallLine + size_.smallSpacing
                                bgColor_: theme.coverColor1
                                textColor_: theme.noColor
                                text_: qsTr("清空")
                                onClicked: imgViewer.clearIg()
                                textSize: size_.smallText
                            }
                        }
                        Text_ {
                            text: ignoreTips
                            color: theme.subTextColor
                            font.pixelSize: size_.smallText
                            anchors.left: parent.left
                            anchors.right: parent.right
                            wrapMode: TextEdit.Wrap
                        }
                    }
                }
            }
        }
        // 右：图片查看面板
        rightItem: ImageWithIgnore {
            id: imgViewer
            anchors.fill: parent
            // 加载中 动态图标
            Loading {
                visible: ocrRunning
                anchors.centerIn: parent
            }
        }
    }
}
