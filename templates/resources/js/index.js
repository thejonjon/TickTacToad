 function api_call(action,data,callback){
	var bid = loadBlip("Running: "+action);
	$.ajax({url: "/api/",type:"POST",data:'action='+action+'&data='+encodeURIComponent(JSON.stringify(data)),async: false,success: function(results){
		objs = jQuery.parseJSON(results);
		if(objs.result=="success"){
			removeBlip(bid,objs.message);
			if(objs.won){
				negBlip("is_it_over!"+objs.won);
				negBlip("is_it_over!"+objs.won);
			}
			$.each(objs.board,function(index,value){
				if(value){
					if(parseInt(value)==parseInt($("#my_id").val())){
						color = "blue";
					}else{
						color = "red";
					}
					$("#tile_"+(index+1)).css('border-color',color);
					$("#tile_"+(index+1)).css('background-image','url("/img/mark.png")');
					
				}
			});
			callback(objs.last_move);
			
		}else{
			removeBlip(bid,objs.message,true);
		}
	}});
}

function vs_computer(name){
	if(!name || name == ""){negBlip("BadName!"); return false;}
	
	var bid = loadBlip("Starting New Game");
	postdata = {"name":name};
	
	$.ajax({url: "/api/",type:"POST",data:'action=vs_computer&data='+encodeURIComponent(JSON.stringify(postdata)),async: true,success: function(results){
		objs = jQuery.parseJSON(results);
		if(objs.result=="success"){
			removeBlip(bid,objs.message);
			window.location = "/game/"+objs.game_id+"/"
		}else{
			removeBlip(bid,objs.message,true);
		}
	}});
}
function claim_tile(tile,callback){
	var tile = $(tile);
	data = {"tile":tile.attr("id"),"game_id":$("#game_id").val()}
	api_call("play",data,callback);
}
