$('#scene_id').on('input', function() { 
	var id = $(this).val(); // get the current value of the input field.
	console.log(id);

	if (id.length == 21){ // it's a pre-collection id
		var path = id.substring(3, 6);
		var row = id.substring(6, 9);
		var year = id.substring(9, 13);
		var thumbnail_url = 'https://earthexplorer.usgs.gov/browse/landsat_8/' + year + '/' + path + '/' + row + '/' + id + '.jpg'
	}
	else if (id.length == 40) { // it's a collection 1 id
		var path = id.substring(10, 13);
		var row = id.substring(13, 16);
		var year = id.substring(17, 21);
		var thumbnail_url = 'https://earthexplorer.usgs.gov/browse/landsat_8/' + year + '/' + path + '/' + row + '/' + id + '.jpg'
	} 

	console.log(thumbnail_url);

	var img = document.getElementById("thumbnail");
	img.onload = function() {
    	// img exists and is loaded, i.e. valid scene id
    	// now load buoy ids that match it
    	update_buoy_ids(id);
	}
	img.onerror = function() {
	    // img did not load
	    img.src = "http://dcokc.org/wp-content/uploads/2015/02/White-Plain-Background-300x300.jpg"
	}

	img.src = thumbnail_url;
});

function update_buoy_ids(scene_id){
	// update list of buoy ids by ajax call and python
	$.ajax({
	    type: 'POST',
	    url: '/buoy_ids',
	    data: { 
	        'scene_id': scene_id
	    },
	    success: function(data){
	        console.log(data);
	        // now change list of buoy ids and maybe the image so that it shows ids
	        var buoy = document.getElementById("buoy_id");

	        buoy.options.length = 0;

	        for (i=0; i < data['ids'].length; i++){
	        	var opt = document.createElement('option');
			    opt.value = data['ids'][i][0];
			    opt.innerHTML = data['ids'][i][1];
	        	buoy.appendChild(opt);
	        }
	    }
	});
}