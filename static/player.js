"use strict";


class Player {
    constructor({$container, videoSrc, videoId, videoStart, videoEnd, isImageSequence, turkMetadata}) {

        this.$container = $container;

        this.videoId = videoId;

        this.selectedAnnotation = null;

        this.annotations = null;

        this.annotationRectBindings = [];

        this.videoSrc = videoSrc;

        this.view = null;

        this.videoStart = videoStart;

        this.videoEnd = videoEnd;

        this.isImageSequence = isImageSequence;

        this.turkMetadata = turkMetadata;

        this.isImageSequence = isImageSequence;

        this.metrics = {
            playerStartTimes: Date.now(),
            annotationsStartTime: null,
            annotationsEndTime: null,
            browserAgent: navigator.userAgent
        };

        // Promises
        this.annotationsDataReady = Misc.CustomPromise();
        this.annotationsReady = Misc.CustomPromise();
        this.viewReady = Misc.CustomPromise();

        // We're ready when all the components are ready.
        this.ready = Misc.CustomPromiseAll(
            this.annotationsReady(),
            this.viewReady()
        );

        // Prevent adding new properties
        Misc.preventExtensions(this, Player);

        this.initAnnotations();
        this.initView();
        this.initHandlers();
    }


    // Init ALL the annotations!

    initView() {
        var {$container, videoSrc, videoStart, videoEnd} = this;

        this.view = new PlayerView({$container, videoSrc, videoStart, videoEnd});

        this.view.ready().then(this.viewReady.resolve);
    }

    initAnnotations() {
        DataSources.annotations.load(this.videoId).then((annotations) => {
            this.annotations = annotations;
            this.annotationsDataReady.resolve();
        });

        // When this.annotations is loaded AND view is ready for drawing...
        Promise.all([this.annotationsDataReady(), this.viewReady()]).then(() => {
            for (let annotation of this.annotations) {
                let rect = this.view.addRect();
                rect.fill = annotation.fill;
                this.initBindAnnotationAndRect(annotation, rect);
            }

            $(this).triggerHandler('change-onscreen-annotations');
            $(this).triggerHandler('change-keyframes');
            this.annotationsReady.resolve();
        });
    }

    initBindAnnotationAndRect(annotation, rect) {
        // On PlayerView...

        this.annotationRectBindings.push({annotation, rect});


        // On Rect...

        $(rect).on('discrete-change', (e, bounds) => {
            annotation.updateKeyframe({
                time: this.view.video.currentTime,
                bounds: bounds,
            }, this.isImageSequence);
            $(this).triggerHandler('change-onscreen-annotations');
            $(this).triggerHandler('change-keyframes');
        });

        $(rect).on('select', () => {
            this.selectedAnnotation = annotation;
            $(this).triggerHandler('change-keyframes');
        });

        $(rect).on('drag-start', () => {
            this.view.video.pause();
        });

        $(rect).on('focus', () => {
            this.selectedAnnotation = annotation;
            $(this).triggerHandler('change-onscreen-annotations');
            $(this).triggerHandler('change-keyframes');
        });


        // On Annotation...

        $(annotation).on('change delete', () => {
            rect.appear({singlekeyframe: annotation.keyframes.length === 1});
        });
        $(annotation).triggerHandler('change');

        $(annotation).on('delete', () => {
            $(annotation).off();
            $(rect).off();
            this.view.deleteRect(rect);
        });
    }

    initHandlers() {
        var thisx = $(this);
            //测试用的数据，这里可以用AJAX获取服务器数据  
        var test_list = [];
        $(function() {
            $("#ischecked").html(document.querySelector('input[name = "object"]:checked').value);
            $('.panel-body .top-controls .label input').each(function(i, e) {
                test_list.push(e.value);
            });            
            old_value = $("#search_text").val();
            $("#search_text").focus(function() {
                if ($("#search_text").val() == "") {
                    // AutoComplete("auto_div", "search_text", test_list);
                }
            });
            $("#search_text").keyup(function(e) {
                if (e.keyCode !== 8 && e.keyCode !== 13) {
                    AutoComplete("auto_div", "search_text", test_list);
                }

            });

        })


        var old_value = "";
        var highlightindex = -1; //高亮  
        //自动完成  
        function AutoComplete(auto, search, mylist) {
            if ($("#" + search).val() != old_value || old_value == "") {
                var autoNode = $("#" + auto); //缓存对象（弹出框）  
                var carlist = new Array();
                var n = 0;
                old_value = $("#" + search).val();
                for (let i in mylist) {
                    if (mylist[i].indexOf(old_value) >= 0) {
                        carlist[n++] = mylist[i];
                    }
                }
                if (carlist.length == 0) {
                    autoNode.hide();
                    return;
                }
                autoNode.empty(); //清空上次的记录  
                for (let i in carlist) {
                    var wordNode = carlist[i]; //弹出框里的每一条内容  
                    var newDivNode = $("<div>").attr("id", i); //设置每个节点的id值  
                    newDivNode.attr("style", "font:14px/25px arial;height:25px;padding:0 8px;cursor: pointer;");
                    newDivNode.html(wordNode).appendTo(autoNode); //追加到弹出框  
                    //鼠标移入高亮，移开不高亮  
                    newDivNode.mouseover(function() {
                        if (highlightindex != -1) { //原来高亮的节点要取消高亮（是-1就不需要了）  
                            autoNode.children("div").eq(highlightindex).css("background-color", "white");
                        }
                        //记录新的高亮节点索引  
                        highlightindex = $(this).attr("id");
                        $(this).css("background-color", "#ebebeb");
                    });
                    newDivNode.mouseout(function() {
                        $(this).css("background-color", "white");
                    });
                    //鼠标点击文字上屏  
                    newDivNode.click(function() {
                        //取出高亮节点的文本内容  
                        var comText = autoNode.hide().children("div").eq(highlightindex).text();
                        highlightindex = -1;
                        //文本框中的内容变成高亮节点的内容  
                        $("#" + search).val(comText);
                        $("#ischecked").html(comText);
                        $('.panel-body .top-controls .label input').each(function(i, e) {
                            if ($('#' + search).val() == e.value) {
                                $('.top-controls label input').removeAttr("checked");
                                $(e).attr('checked', 'true');
                            }
                        })

                        thisx.triggerHandler('change-onscreen-annotations');
                        thisx.triggerHandler('change-keyframes');
                    })
                    if (carlist.length > 0) { //如果返回值有内容就显示出来  
                        autoNode.show();
                    } else { //服务器端无内容返回 那么隐藏弹出框  
                        autoNode.hide();
                        //弹出框隐藏的同时，高亮节点索引值也变成-1  
                        highlightindex = -1;
                    }
                }
            }
            //点击页面隐藏自动补全提示框  
            document.onclick = function(e) {
                var e = e ? e : window.event;
                var tar = e.srcElement || e.target;
                if (tar.id != search) {
                    if ($("#" + auto).is(":visible")) {}
                }
            }
        }

        $('input[type=radio][name=object]').change(
            function(){
                thisx.triggerHandler('change-onscreen-annotations');
                thisx.triggerHandler('change-keyframes');
            }
        )
        // Drawing annotations
        $(this).on('change-onscreen-annotations', () => {
            this.drawOnscreenAnnotations();
        });

        $(this).on('change-keyframes', () => {
            this.drawKeyframes();
        });


        // Submitting
        $('#submit-btn').click(this.submitAnnotations.bind(this));

        $('#btn-show-accept').click(this.showAcceptDialog.bind(this));
        $('#btn-show-reject').click(this.showRejectDialog.bind(this));
        $('#btn-show-email').click(this.showEmailDialog.bind(this));

        $('#accept-reject-btn').click(this.acceptRejectAnnotations.bind(this));

        $('#email-btn').click(this.emailWorker.bind(this));

        $("#frameRate").on("keyup",function(){
            $(this).val($(this).val().replace(/[^\d{1,}\.\d{1,}|\d{1,}]/g,''));
            if($(this).val()>60){
                $(".input_alert").show();
                $(this).val(0.04);
            }else{
                $(".input_alert").hide();
            }
        })
        $(".close_tip").click(function(){
            $(".input_alert").hide()
        });
        // On drawing changed
        this.viewReady().then(() => {
            $(this.view.creationRect).on('drag-start', () => {
                this.view.video.pause();
            });

            $(this.view.creationRect).on('focus', () => {
               this.selectedAnnotation = null;
                $(this).triggerHandler('change-onscreen-annotations');
                $(this).triggerHandler('change-keyframes');
            });

            this.view.video.onTimeUpdate(() => {
                $(this).triggerHandler('change-onscreen-annotations');
            });

            $(this.view).on('create-rect', (e, rect) => {
                this.addAnnotationAtCurrentTimeFromRect(rect);
                rect.focus();
                $(this).triggerHandler('change-keyframes');
            });

            $(this.view).on('delete-keyframe', () => {
                this.view.video.pause();
                this.deleteSelectedKeyframe();
                $(this).triggerHandler('change-onscreen-annotations');
                $(this).triggerHandler('change-keyframes');
            });

            $(this.view).on('step-forward-keyframe', () => {
                var time = this.view.video.currentTime;
                if (!this.selectedAnnotation || !this.selectedAnnotation.keyframes)
                    return;
                for (let [i, kf] of this.selectedAnnotation.keyframes.entries()) {
                    if (Math.abs(time - kf.time) < this.selectedAnnotation.SAME_FRAME_THRESHOLD) {
                        if (i != this.selectedAnnotation.keyframes.length - 1) {
                            var nf = this.selectedAnnotation.keyframes[i + 1];
                            this.view.video.currentTime = nf.time;
                            break;
                        }
                    }
                }
            });

            $(this.view).on('step-backward-keyframe', () => {
                var time = this.view.video.currentTime;
                var selected = this.selectedAnnotation;
                if (!this.selectedAnnotation || !this.selectedAnnotation.keyframes)
                    return;
                for (let [i, kf] of this.selectedAnnotation.keyframes.entries()) {
                    if (Math.abs(time - kf.time) < this.selectedAnnotation.SAME_FRAME_THRESHOLD) {
                        if (i !== 0) {
                            var nf = this.selectedAnnotation.keyframes[i - 1];
                            this.view.video.currentTime = nf.time;
                            break;
                        }
                    }
                }
            });

            $(this.view).on('duplicate-keyframe', () => {
                var time = this.view.video.currentTime;

                if (!this.selectedAnnotation || !this.selectedAnnotation.keyframes) {
                    return;
                }
                var previousKeyFrame;
                for (let [i, kf] of this.selectedAnnotation.keyframes.entries()) {
                    if (Math.abs(kf.time - time) < this.selectedAnnotation.SAME_FRAME_THRESHOLD) {
                        return;
                    } else if (kf.time > time) {
                        break;
                    }
                    previousKeyFrame = kf;
                }
                this.selectedAnnotation.updateKeyframe({time:time, bounds:previousKeyFrame.bounds}, this.isImageSequence);
                $(this).triggerHandler('change-onscreen-annotations');
                $(this).triggerHandler('change-keyframes');
            });

        });
    }

    
    // Draw something

    drawOnscreenAnnotations() {
        var isNameMatched = document.querySelector('input[name = "object"]:checked').value;
        for (let {annotation, rect} of this.annotationRectBindings) {
            this.drawAnnotationOnRect(annotation, rect, isNameMatched);
        }
    }

    drawKeyframes() {
        this.view.keyframebar.resetWithDuration(this.view.video.duration);
        var str = "",key_number= 0;
        var nameselected = document.querySelector('input[name = "object"]:checked').value;
        for (let annotation of this.annotations) {
            str += "<p>"+annotation.type+","+annotation.keyframes.length+"</p>";
            var isNameMatched = (nameselected === annotation.type);
            if(isNameMatched){
                key_number += annotation.keyframes.length;
            }
            for (let keyframe of annotation.keyframes) {
                let selected = (annotation == this.selectedAnnotation);
                this.view.keyframebar.addKeyframeAt(keyframe.time, {selected,isNameMatched});
            }
        }
        $("#ischecked").html(nameselected+"("+key_number+")");
        $("#salary").html(str);
        $("#type_num").html(this.annotations.length);
        $("#slide_button").click(function(){
            $("#salary").toggle();
        });
    }

    drawAnnotationOnRect(annotation, rect, isNameMatched) {
        if (this.metrics.annotationsStartTime == null) {
            this.metrics.annotationsStartTime = Date.now();
            // force the keyboard shortcuts to work within an iframe
            window.focus();
        }
        var time = this.view.video.currentTime;

        var {bounds, prevIndex, nextIndex, closestIndex, continueInterpolation} = annotation.getFrameAtTime(time, this.isImageSequence);

        // singlekeyframe determines whether we show or hide the object
        // we want to hide if:
        //   - the very first frame object is in the future (nextIndex == 0 && closestIndex is null)
        //   - we're after the last frame and that last frame was marked as continueInterpolation false
        rect.appear({
            real: closestIndex != null,
            selected: this.selectedAnnotation === annotation,
            singlekeyframe: continueInterpolation && !(nextIndex == 0 && closestIndex === null),
            nameselected: isNameMatched === annotation.type,
        });

        // Don't mess up our drag
        if (rect.isBeingDragged()) return;

        rect.bounds = bounds;
    }


    // Actions

    submitAnnotations(e) {
        e.preventDefault();
        this.metrics.annotationsEndTime = Date.now();
        if (this.metrics.annotationsStartTime == null) {
            this.metrics.annotationsStartTime = this.metrics.annotationsEndTime;
        }
        if (this.annotations.length === 0 && !confirm('Confirm that there are no objects in the video?')) {
            return;
        }
        DataSources.annotations.save(this.videoId, this.annotations, this.metrics, window.mturk).then((response) => {
            // only show this if not running on turk
            if (!window.hitId)
                this.showModal("Save", response);
        });
    }

    showModal(title, message) {
        $('#genericModalTitle')[0].innerText = title;
        $('#genericModalMessage')[0].innerText = message;
        $('#genericModal').modal();
    }

    showAcceptDialog(e) {
        this.setDialogDefaults();
        if (this.turkMetadata) {
            $('#inputAcceptRejectMessage')[0].value = this.turkMetadata.bonusMessage
        }
        $('#acceptRejectType')[0].value = 'accept';
        $('#labelForBonus').text("Bonus")
        $('#inputBonusAmt').prop('readonly', false);
        $('#inputReopen')[0].checked = false;
        $('#inputDeleteBoxes')[0].checked = false;
        $('#inputBlockWorker')[0].checked = false;
        $('#accept-reject-btn').removeClass('btn-danger').addClass('btn-success')
        $('#accept-reject-btn').text('Accept');
        $('#acceptRejectForm').find('.modal-title').text("Accept Work");
        $('#acceptRejectForm').modal('toggle');
    }
    showRejectDialog(e) {
        this.setDialogDefaults();
        if (this.turkMetadata) {
            $('#inputAcceptRejectMessage')[0].value = this.turkMetadata.rejectionMessage;
        }
        $('#acceptRejectType')[0].value = 'reject';
        $('#labelForBonus').text("Lost Bonus")
        $('#inputBonusAmt').prop('readonly', true);
        $('#inputReopen')[0].checked = true;
        $('#inputDeleteBoxes')[0].checked = true;
        $('#inputBlockWorker')[0].checked = false;
        $('#accept-reject-btn').removeClass('btn-success').addClass('btn-danger')
        $('#accept-reject-btn').text('Reject');
        $('#acceptRejectForm').find('.modal-title').text("Reject Work");
        $('#acceptRejectForm').modal('toggle');
    }
    setDialogDefaults(){
        if (this.turkMetadata) {
            $('#inputBonusAmt')[0].value = this.turkMetadata.bonus
            $('.workerTime').text(this.verbaliseTimeTaken(this.turkMetadata.storedMetrics));
            $('.readonlyBrowser').text(this.turkMetadata.storedMetrics.browserAgent);
        }
        else {
            $('.turkSpecific').css({display:'none'});
        }
    }

    showEmailDialog(e) {
        this.setDialogDefaults();

        $('#inputEmailMessage')[0].value = this.turkMetadata.emailMessage;
        $('#inputEmailSubject')[0].value = this.turkMetadata.emailSubject;
        $('#emailForm').modal('toggle');
    }

    verbaliseTimeTaken(metricsObj) {
        var timeInMillis = metricsObj.annotationsEndTime - metricsObj.annotationsStartTime;

        return Math.round(timeInMillis / 60 / 100) / 10 + " minutes";
    }

    acceptRejectAnnotations(e) {
        e.preventDefault();
        var bonus = $('#inputBonusAmt')[0];
        var message = $('#inputAcceptRejectMessage')[0];
        var reopen = $('#inputReopen')[0];
        var deleteBoxes = $('#inputDeleteBoxes')[0];
        var blockWorker = $('#inputBlockWorker')[0]
        var type = $('#acceptRejectType')[0].value;

        $('#acceptRejectForm').find('.btn').attr("disabled", "disabled");

        var promise;
        if (type == 'accept')
            promise = DataSources.annotations.acceptAnnotation(this.videoId, parseFloat(bonus.value), message.value,
                                                               reopen.checked, deleteBoxes.checked, blockWorker.checked, this.annotations);
        else
            promise = DataSources.annotations.rejectAnnotation(this.videoId, message.value, reopen.checked, deleteBoxes.checked, blockWorker.checked, this.annotations);

        promise.then((response) => {
            $('#acceptForm').modal('toggle');
            $('#acceptForm').find('.btn').removeAttr("disabled");
            location.reload();
        }, (err) => {
            alert("There was an error processing your request.");
            $('#acceptForm').find('.btn').removeAttr("disabled");
        });
    }

    emailWorker(e) {
        e.preventDefault();
        var subject = $('#inputEmailSubject')[0];
        var message = $('#inputEmailMessage')[0];

        $('#emailForm').find('.btn').attr("disabled", "disabled");
        DataSources.annotations.emailWorker(this.videoId, subject.value, message.value).then((response) => {
            $('#emailForm').modal('toggle');
            $('#emailForm').find('.btn').removeAttr("disabled");
            location.reload();
        }, (err) => {
            alert("There was an error processing your request:\n" + err);
            $('#emailForm').find('.btn').removeAttr("disabled");
        });
    }

    addAnnotationAtCurrentTimeFromRect(rect) {
        var annotation = Annotation.newFromCreationRect(this.isImageSequence);
        annotation.updateKeyframe({
            time: this.view.video.currentTime,
            bounds: rect.bounds
        }, this.isImageSequence);
        this.annotations.push(annotation);
        rect.fill = annotation.fill;
        this.initBindAnnotationAndRect(annotation, rect);
    }

    deleteAnnotation(annotation) {
        if (annotation == null) return false;

        if (annotation == this.selectedAnnotation) {
            this.selectedAnnotation = null;
        }

        for (let i = 0; i < this.annotations.length; i++) {
            if (this.annotations[i] === annotation) {
                annotation.delete();
                this.annotations.splice(i, 1);
                this.annotationRectBindings.splice(i, 1);
                return true;
            }
        }

        throw new Error("Player.deleteAnnotation: annotation not found");
    }

    deleteSelectedKeyframe() {
        if (this.selectedAnnotation == null) return false;
        var selected = this.selectedAnnotation;
        this.selectedAnnotation = null;
        selected.deleteKeyframeAtTime(this.view.video.currentTime, this.isImageSequence);

        if (selected.keyframes.length === 0) {
            this.deleteAnnotation(selected);
        }

        return true;
    }
}

void Player;
