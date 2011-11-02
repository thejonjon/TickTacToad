//Position related-- 
function findPosX(obj){
	obj = document.getElementById($(obj).attr('id'));
	var curleft = 0;
	if(obj.offsetParent){
		while(1){
			curleft += obj.offsetLeft;
			if(!obj.offsetParent){break;}
			obj = obj.offsetParent;
		}
	}else if(obj.x){
		curleft += obj.x;
	}
	return curleft;
}

function findPosY(obj){
	obj = document.getElementById($(obj).attr('id'));
	var curtop = 0;
	if(obj.offsetParent){
		while(1){
			curtop += obj.offsetTop;
			if(!obj.offsetParent){break;}
			obj = obj.offsetParent;
		}
	}else if(obj.y){
		curtop += obj.y;
	}
	return curtop;
}


//============BLIP RELATED===============
function removeBlip(id,text,error,timeout){
	//Used for removing blips that say: Loadinng or what have you
	//id of the blip
	//text to overrrite the blip with
	//(optional) if error is true then make text red-- otherwise stay black
	//(optional) timeout is ann optional time out to how many ms the message stays there
	if(!timeout){
		timeout = 5000;
	}

	if(error==true){
		$("#blip_"+id).css('color','red');
	}
	if(text){
		$("#blip_"+id).html(text);
	}
	if(timeout!=-1){
		$("#blip_"+id).delay(timeout).slideUp('fast',function(){
			$(this).remove();
		});
	}else{
		$("#blip_"+id).html("<span style='float:right;' class='blip_x'>X</span>"+text);
	}
		
}
messageBlip = function (text,type,timeout) {
	if(!timeout){
		timeout=4000;
	}
	var randomnumber=Math.floor(Math.random()*999999)
	if(type=="loading"){
		$('#blipbox').prepend("<div id='blip_"+randomnumber+"' class='message_blip'><img src='/img/loading.gif' style='float:left; padding-top:3px;'>"+text+"</div>");
		$("#blip_"+randomnumber).slideDown(100);
		return randomnumber;
	}else if(type=="neg"){
		$('#blipbox').prepend("<div id='blip_"+randomnumber+"' class='message_blip' style='color:red;'><span style='float:right;' class='blip_x'>X</span>"+text+"</div>");
	} else {
		$('#blipbox').prepend("<div id='blip_"+randomnumber+"' class='message_blip' style='color:green;'><span style='float:right;' class='blip_x'>X</span>"+text+"</div>");
	}
	
	$("#blip_"+randomnumber).slideDown('fast',function(){
		if(timeout!=-1){
			$(this).delay(timeout).slideUp('fast',function(){
				$(this).remove();
			});
		}
	});
};
function posBlip(text,time){messageBlip(text,"pos",time);}
function negBlip(text,time){messageBlip(text,"neg",time);}
function loadBlip(text,time){ return messageBlip(text,"loading",time);}

//Player Object===================================
function Player(element,home) {
	var bouncing = false;
	var moving = false;
	this.homex = parseInt(findPosX($(home)));
	this.homey = parseInt(findPosY($(home)));
	this.returnHome = function(callback){
		if(this.homex && this.homey){
			this.move(this.homex,this.homey,callback);
			
		}
	}
	this.bounce = function(){
		var bouncing = bouncing;
		if(!moving){
			bouncing=true;
			$(element).effect( "bounce", { }, 300,function(){
				bouncing=false;
			});
		}
	}
	
	this.move = function(x,y,callback){
		var callback = callback;
		if(!bouncing){
			element.stop();
		}
		element.animate({left:x+"px",top:y+"px"},callback);
	}
	this.toTile = function(tile,callback){
		this.move(findPosX(tile)+6,findPosY(tile),callback);
	}
	this.madeMove = function(tile){
		tile.css('border-color','blue');
		tile.css('background-image','url("/img/mark.png")');
	}

	this.claimTile = function(tile,callback){
		this.toTile(tile,callback);
	}
	
	
}

