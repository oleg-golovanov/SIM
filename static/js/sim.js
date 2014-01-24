var levels = {
    1: 'info',
    2: 'warning',
    3: 'error',
    4: 'critical',
    'info': 1,
    'warning': 2,
    'error': 3,
    'critical': 4
};

var change_counter = function(level, action) {
    var counter_item = $('#' + levels[level] + '-counter');
    var counter = parseInt(
        counter_item.text()
    );
    if (action == 0) {
        counter_item.text(--counter);
    } else if (action == 1) {
        counter_item.text(++counter);
    }
};

var add_message = function(message) {
    var messages = $('#' + levels[message['priority']] + '-messages');
    messages.prepend(
        '<li id="' + message['rowid'] + '" class="message">' +
            '<div class="row-fluid">' +
                '<div class="span4 tech_info">' +
                    message['time'] + '<br>' +
                    message['source'] +
                '</div>' +
                '<div class="span8">' +
                    '<button type="button" class="close pull-right">&times</button>' +
                    message['text'] +
                '</div>' +
            '</div>' +
        '</li>'
    );

    change_counter(message['priority'], 1);

    if (messages.hasClass('open') == true) {
        var item = $('#' + message['rowid']);
        item.hide().fadeIn();
    }
};

var del_message = function(number) {
    var item = $('#' + number);
    var item_parent = item.parent();
    var level = levels[
        item_parent.attr('id').split('-')[0]
    ];

    change_counter(level, 0);
    item.slideUp(
        function() {item.remove()}
    );
};

ws.onerror = function(data) {
    alert(
        "Can't connect to " + data.target.url
    );
};
ws.onmessage = function(data) {
    var message = JSON.parse(data.data);
    if (typeof message == 'number') {
        del_message(message);
    } else if (typeof message == 'object') {
        add_message(message);
    }
};

$(document).ready(function() {

	var render_list = function() {
        $.getJSON("/messages/", function(data) {
            for (var i = 0; i < data.length; i++) {
                add_message(data[i])
            }
            $('ul').hide();
        });
    };

    $('ul').delegate(
		'.close',
		'click',
		function() {
			var item = $(this).parents('li');
			var id = item.attr('id');
            $.ajax({
                url: '/messages/?id=' + id,
                type: 'DELETE'
            });
		}
	);

    $('.well').delegate(
        '',
        'click',
        function() {
            var level = $(this).attr('id').split('-')[0];
            var messages = $('#' + level + '-messages');
            var arrow = $(this).find('i');
            arrow.toggleClass('icon-chevron-right icon-chevron-down');
            messages.toggleClass('open');
            messages.slideToggle();
        }
    );

	render_list();
});
