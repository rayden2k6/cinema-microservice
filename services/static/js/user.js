function time(s) {
    return new Date(s * 1e3).toISOString().slice(-13, -5);
}
function update_table() {
    $.getJSON( "/users", function( data ) {
        var keys = Object.keys(data);
        //console.log(keys)
        // console.log(keys)
        var items = [];
        var value = "";
        for(var count = 0; count < keys.length; count ++) {
            var key = keys[count];
            if (key in data) {
                var _object = data[key];
                var name = _object['name'];
                var last_active = time(parseInt(_object['last_active']));
                value += "<tr>" + "<td>" + key + "</td>" + "<td>" + name + "</td>" + "<td>" + last_active + "</td>" + "</tr>"
            }
            var table = document.getElementById('contents');
            table.innerHTML = value;
        }
    });

}

function add_user() {
    $(document).on("click", "#add-user-button", function (e) {
        $('#main-list').css('display', 'none');
        $('#sub-main-list').css('display', '');
    });
    $(document).on("click", ".cancel-button", function (e) {
        e.preventDefault();
        window.location = '/';
    });
    $(document).on('click', '#create-button', function (e) {
        e.preventDefault();
        $.post({
            url: '/users/add',
            data: $('#create-user-form').serialize(),
            success: function (data) {
                console.log(data);
                window.location = '/';
            },
            error: function (error) {
                window.location = '/';
            }
        });
    });
    $(document).on('click', '#contents > tr', function (e) {
        $('#main-list').css('display', 'none');
        $('#update-list').css('display', '');
        $('#update-user-form').find('#inputUserId').val($(this).find('td:nth-child(1)').text());
        $('#update-user-form').find('#inputUserName').val($(this).find('td:nth-child(2)').text());
    });

    $(document).on('click', '#update-button', function (e) {
        e.preventDefault();
        $.ajax({
            url: "/users/update",
            type: 'POST',
            data: {
                id: $('#update-user-form').find('#inputUserId').val(),
                name: $('#update-user-form').find('#inputUserName').val()
            },
            success: function (data) {
                window.location = '/';
            },
            error: function (data) {
                window.location = '/';
            }
        });
    });

    $(document).on('click', '#delete-button', function (e) {
        e.preventDefault();
        $.ajax({
            url: "/users/delete",
            type: 'DELETE',
            data: {
                id: $('#update-user-form').find('#inputUserId').val(),
                name: $('#update-user-form').find('#inputUserName').val()
            },
            success: function (data) {
                window.location = '/';
            },
            error: function (data) {
                window.location = '/';
            }
        });
    });
}

$(document).ready(function (e) {
    update_table();
    add_user();
});