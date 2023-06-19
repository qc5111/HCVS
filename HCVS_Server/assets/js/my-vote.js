let page = 1;
let choiceNum = 1;
function showCreateScreen(){
    $('#create-modal').modal();
}
function calcDuration(startDate,endDate){
  const timeDifference = Math.abs(endDate - startDate);

  // 计算时间差的日、小时和分钟
  const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
  const hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
  return {days, hours, minutes};
}
function calcTimeDiff(){
    let startTime = $('#StarTime').val();
    let endTime = $('#EndTime').val();
    if (startTime === '' || endTime === ''){
        return;
    }
  let startDate = new Date(startTime);
  let endDate = new Date(endTime);
  let diffDate = calcDuration(startDate,endDate);
  $('#Duration').html(diffDate["days"] + "days " + diffDate["hours"] + "hours " + diffDate["minutes"] + "minutes");
}
function flashChoice(){
    let $choice = $('.Choice');
    $('.optionButton').remove();
    console.log($choice.length);
    for (let i = 0; i < $choice.length; i++){
        $tdList = $($choice[i]).find('td')
        $tdList[0].innerHTML="Choice " + (i+1);
        $tdList[1].firstChild.id = "Choice" + (i+1);
        $($tdList[1]).find('input').attr('seq', i+1);
        //增加删除按钮
        if (choiceNum > 1){
            let $delBtn = $('<a class="optionButton" href="javascript:delChoice('+(i+1)+')"><span class="am-icon-minus" style="width: 10%"></span></a>');
            $($tdList[1]).append($delBtn);
        }
        //增加增加按钮
        if (i === $choice.length - 1){
            $($tdList[1]).find('input').attr('style', 'width: 60%');
            let $addBtn = $('<a class="optionButton" href="javascript:addChoice()"><span class="am-icon-plus" style="width: 10%"></span></a>');
            $($tdList[1]).append($addBtn);
        }else{
            $($tdList[1]).find('input').attr('style', 'width: 70%');
        }
    }
}
function addChoice(){
    if(choiceNum >= 32){
        alert("Too many choices!");
        return;
    }
    let $newTr = $('<tr class="Choice"></tr>');
    let $newLabel = $("<td>Choice2</td>");
    let $newTd = $("<td></td>");
    let $choice = $('#Choice1');
    let $voteOption = $('#vote-option');
    let $newChoice = $choice.clone();
    $newChoice.attr('id', '');
    $newChoice.val('');
    $newTd.append($newChoice);
    $newTr.append($newLabel);
    $newTr.append($newTd);
    $voteOption.append($newTr);
    choiceNum++;
    flashChoice();
}
function delChoice(seq){
    let $choice = $('#Choice' + seq);
    $choice.parent().parent().remove();
    choiceNum--;
    flashChoice();
}
function createVote(){
    let voteName = $('#voteName').val();
    let startTime = Date.parse($('#StarTime').val());
    let endTime = Date.parse($('#EndTime').val());
    let minChoice = parseInt($('#minChoice').val());
    let maxChoice = parseInt($('#maxChoice').val());
    let choiceList = {};
    for (let i = 0; i < choiceNum; i++){
        let choice = $('#Choice' + (i+1)).val();
        if (choice === ''){
            alert("Choice can't be empty!");
            return;
        }
        choiceList[parseInt(i+1)] = choice;
    }
    if (voteName === ''){
        alert("Vote name can't be empty!");
        return;
    }
    if (isNaN(startTime) || isNaN(endTime)){
        alert("Time can't be empty!");
        return;
    }
    if (isNaN(minChoice)||isNaN(maxChoice)){
        alert("Choice number can't be empty!");
        return;
    }
    if (minChoice > maxChoice){
        alert("Min choice number can't be greater than max choice number!");
        return;
    }
    if (minChoice < 1 || maxChoice < 1){
        alert("Choice number can't be less than 1!");
        return;
    }
    if (minChoice >= choiceNum || maxChoice >= choiceNum){
        alert("Choice number can't be greater than choice number!");
        return;
    }
    // 检查选项是否重复
    for(let key in choiceList){
        if (choiceList[key] === ''){
            alert("Choice can't be empty!");
            return;
        }
        for(let key2 in choiceList){
            if (key !== key2 && choiceList[key] === choiceList[key2]){
                alert("Choice can't be the same!");
                return;
            }
        }
    }
    //构建提交json
    let data = {
        voteName: voteName,
        startTime: startTime,
        endTime: endTime,
        minChoice: minChoice,
        maxChoice: maxChoice,
        choiceList: choiceList
    };
    //console.log(data);


    $.ajax({
        url: "/admin/create-vote",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(data),

        success: function(data){
            if (data.success){
                alert("Create vote success!\nID: " + data.voteId);
                window.location.href = "/admin/vote-management";
            }
        }
    });
}
$(function(){
    $('#create-modal').on('close.modal.amui', function(){
        keyInfoClose();
    });
});

function keyInfoClose(){
    let $keyInfo = $('#key-info');
    $keyInfo.html('');
    getVote();
}
function getVote(){
    $.ajax({
        url: "/admin/get-vote-list",
        type: "GET",

        data: {
            page: page,
            filter: $('#filter').val()
        },
        success: function(data){
            console.log(data);
            $voteList = $('#vote-list');
            //清空
            $voteList.html('');
            //遍历并添加元素
            for(let i = 0; i < data["voteList"].length; i++){
                let $tr = $('<tr></tr>');
                let $tdId = $('<td></td>');
                let $tdVoteName = $('<td></td>');
                let $tdStartTime = $('<td></td>');
                let $tdEndTime = $('<td></td>');
                let $tdDuration = $('<td></td>');
                let $tdMinChoice = $('<td></td>');
                let $tdMaxChoice = $('<td></td>');
                let $tdChoices = $('<td></td>');
                let $tdCreator = $('<td></td>');
                let $tdStatus = $('<td></td>');
                let StartTime = new Date(data["voteList"][i]["start_time"]);
                let EndTime = new Date(data["voteList"][i]["end_time"]);
                let NowTime = new Date();
                let diffDate = calcDuration(StartTime,EndTime);
                $tdId.html(data["voteList"][i]["id"]);
                $tdVoteName.html(data["voteList"][i]["name"]);
                $tdStartTime.html(StartTime.toLocaleString());
                $tdEndTime.html(EndTime.toLocaleString());
                $tdDuration.html(diffDate["days"] + "days " + diffDate["hours"] + "hours " + diffDate["minutes"] + "minutes");
                $tdMinChoice.html(data["voteList"][i]["min_choice"]);
                $tdMaxChoice.html(data["voteList"][i]["max_choice"]);
                for(let key in data["voteList"][i]["choiceList"]){
                    $tdChoices.append(data["voteList"][i]["choiceList"][key] + "<br>");
                }
                $tdCreator.html(data["voteList"][i]["createUser"]);
                if (StartTime > NowTime){
                    $tdStatus.html("<span style='color: deepskyblue'>Not Started</span>");
                }
                else if (EndTime < NowTime){
                    $tdStatus.html("<span style='color: red'>Ended</span>");
                }
                else{
                    $tdStatus.html("<span style='color: green'>In Progress</span>");
                }
                $tr.append($tdId);
                $tr.append($tdVoteName);
                $tr.append($tdStartTime);
                $tr.append($tdEndTime);
                $tr.append($tdDuration);
                $tr.append($tdMinChoice);
                $tr.append($tdMaxChoice);
                $tr.append($tdChoices);
                $tr.append($tdCreator);
                $tr.append($tdStatus);


                $voteList.append($tr);
            }
            //更新总数与页数

            $pageControl = $('#page-control');
            $('#total').html('Total Matched: ' + data["totalVote"]);
            $pageControl.html('');
            let $liPrevious = $('<li><a href="javascript:PreviousPage()">«</a></li>');
            let $liNext = $('<li><a href="javascript:NexPage()">»</a></li>');
            if (page === 1){
                $liPrevious.addClass('am-disabled');
            }
            $pageControl.append($liPrevious);
            let showMinPage = page - 2;
            if (showMinPage < 1){
                showMinPage = 1;
            }
            for(let i = showMinPage; i <= showMinPage + 4; i++){
                let $li = $('<li><a href="#">' + i + '</a></li>');
                if (i === page){
                    $li.addClass('am-active');
                }
                $pageControl.append($li);
            }
            $pageControl.append($liNext);
        }
    });
}

function NexPage(){
    page++;
    getVote();
}
function PreviousPage(){
    if (page > 1){
        page--;
    }
    getVote();
}
//添加搜索框回车事件
$('#filter').bind('keypress',function(event){
    if(event.keyCode == "13")
    {
        getVote();
    }
});