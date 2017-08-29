window.onload = enumerate_tasks;

function enumerate_tasks() {
    console.log("enumerate_tasks been called");

    // GET request async, python return is first arg with attributes
    $.getJSON('/enum_tasks', {},
        function(data) {
            // enumerate active tasks
            tasks = data.tasks;
            console.log(tasks);

            for (i=0; i < tasks.length; i++) {
                // generate url, build progressbars
                var status_url = '/status/' + tasks[i]['task_id'];
                console.log(status_url);
                create_progress_bar(status_url);
            }
        }
    );
}


function create_progress_bar(status_url) {
    // add task status elements
    console.log("create_progress_bar been called");

    div = $('<div class="progress"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div><hr>');
    $('#progress').append(div);

    // create a progress bar
    var nanobar = new Nanobar({
        bg: '#44f',
        target: div[0].childNodes[0]
    });

    update_progress(status_url, nanobar, div[0]);
}


function update_progress(status_url, nanobar, status_div) {
    console.log("update_progress been called");

    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        nanobar.go(percent);
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text(data['status']);
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                // show result
                $(status_div.childNodes[3]).text('Result: ' + data['result']);
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 1 seconds
            setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
            }, 1000);
        }
    });
}