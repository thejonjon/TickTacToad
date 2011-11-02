
$(document).ready(function(){
	
	var sam = new Player($("#sam"),$("#human_spot"));
	var human = new Player($("#you"),$("#sam_spot"));
	sam.returnHome(); human.returnHome();
	//you.bounce();
	//alert(findPosX($("#tile_2"))+","+findPosY($("#tile_2")));
	//them.move(findPosX($("#tile_2")),findPosY($("#tile_2")));
	//them.toTile($("#tile_4"));
	
	
	$(".tile").click(function(){
		tile = $(this);
		human.toTile($(this),function(){
			claim_tile(tile,function(what){
				if(what){sam.toTile($("#tile_"+what),function(){sam.returnHome();});}
				human.returnHome();
			});
		});
	});
});
