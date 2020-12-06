document.addEventListener("DOMContentLoaded", () => {
	if (document.querySelectorAll('.result').length < 20) {
    npb.disabled = true;
    hnpb.disabled = true;
    lpb.disabled = true;
    hlpb.disabled = true;
  }
	if (ppf.value == '0') {
    ppb.disabled = true;
    fpb.disabled = true;
    hppb.disabled = true;
    hfpb.disabled = true;
  }
  replaceImageFailures();
  timeline();
})
const replaceImageFailures = () => {
  r = /(i?)\.(jpg|png|gif)$/i;
  const images = document.querySelectorAll(".thumb img");
  for (let i of images) {
    console.log(i)
    if(i.getAttribute("src").search(r) == -1) {
      i.src = "/static/images/missing_image.png"
    }
  }
}
const timeline = () => {
	sortedDates = results.map(a => a[1]).sort()
	oldest = Number(sortedDates[0])
	youngest = Number(sortedDates[results.length-1])
	unique = [...new Set(sortedDates)]

	const myCanvas=document.getElementById('timeLine');
	var w = myCanvas.clientWidth;
	myCanvas.width = w;
	var h = myCanvas.clientHeight;
	myCanvas.height = h;
	const canvasDrawer = myCanvas.getContext('2d');
	canvasDrawer.lineCap='round'
	canvasDrawer.font = '30px Ariel'
	canvasDrawer.strokeStyle='#eee';
	canvasDrawer.fileStyle='#eee';
	canvasDrawer.lineWidth=2;
	
	
	var range = youngest-oldest+2;//add 2 years for the top and bottom bracket
	if (range<10){//if the range is uncomfertably small then make it bigger
		oldest -= 4;
		youngest += 4;
		range+=8;
	}
	var spacing = (h-40)/range;//the spacing between years on the timeline
	var filled = []; //an array containing the # of objects at place [index]
	
	drawBase(oldest,youngest)
	results.forEach(drawGames)
	
	function drawBase(min, max) {
		var gap = 1;//the distance between years marked
		while ((range/gap) > 20){//<- put the max number of ticks here
		gap++;
		}
		//draw the big tabs and center tab
		
			canvasDrawer.beginPath();
			canvasDrawer.moveTo(w/2,0);
			canvasDrawer.lineTo(w/2+10,20);
			canvasDrawer.lineTo(w/2-10,20);
			canvasDrawer.closePath();
		canvasDrawer.stroke()
		canvasDrawer.beginPath();
			canvasDrawer.moveTo(w/2,h);
			canvasDrawer.lineTo(w/2+10,h-20);
			canvasDrawer.lineTo(w/2-10,h-20);
			canvasDrawer.closePath();
		canvasDrawer.stroke()
		canvasDrawer.moveTo(w/2,20);
		canvasDrawer.lineTo(w/2,h-20);
		canvasDrawer.stroke();
		//draw the middle tabs
		for (var i = 0; i <= youngest-oldest; i+=gap){
		 canvasDrawer.moveTo(w/5*2,spacing*(i+1)+20);
		 canvasDrawer.lineTo(w/5*3,spacing*(i+1)+20);
		 canvasDrawer.strokeText((oldest+(i)),w/3*2+10,spacing*(i+1)+20);
		}
		canvasDrawer.stroke();//stroke is basicaly the commit function
	}
	//0-name 1-date 2-pub 3-GID 4-console 5-image
	function drawGames(item, index){
		console.log(item)
		var place =Number(item[1])-(oldest-1);//2 is added for the top & bottom spacing
		
		if (filled[place]==undefined){
			filled[place]=1
		}else{
			filled[place]+=1
		}
		
		var veriticalPlace = filled[place]
		console.log(veriticalPlace);
		picture = document.getElementById(item[3]);
		clone = picture.cloneNode(true);
		clone.style.maxHeight = (h/21).toString()+"px";
		clone.style.maxWidth = (w/6).toString()+"px";
		clone.style.top = (place*spacing+(veriticalPlace%2*10)-5).toString()+"px";
		clone.style.left = (w/2-(veriticalPlace*50)).toString()+"px";
		clone.style.zIndex = item[3].toString(); //setting the z index to the gid //doesnt actually matter as long as unique > 0 value
		myCanvas.parentElement.insertBefore(clone,myCanvas);
	}
}