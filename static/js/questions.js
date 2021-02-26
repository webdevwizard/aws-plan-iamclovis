var que_cnt = 22;

function getQuizCount() {
    return que_cnt;
}

var cur_que = 1;

function get_cur_que() {
    return cur_que;
}

function set_cur_que(cur) {
    return cur_que = cur;
}

function submit_data() {
    var data = JSON.stringify(user_answer)
    $('<input type="hidden" name="json"/>').val(data).appendTo('#data_submit');
    $("#data_submit").submit();
}

var ans_map = [0, 1, 2, 2, 3, 3, 3, 4, 5, 6, 7, 8, 9, 10, 11];
var ans_dis = [0, 0, 0,    0,       0, 0, 0, 0, 0, 0, 0,  0];

var user_answer = {
    gastric_bypass: 'no',
    pregnant: 'no',
    hundred_pounds: 'no'
};

var measurements = {
    gender: "",
    age: "",
    height: "",
    weight: "",
    activity_level: "",
    health_goal: "",
};
