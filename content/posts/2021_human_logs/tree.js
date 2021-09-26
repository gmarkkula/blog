var T = 1;
var GROWTHT = T * 3;
var EXTT = T * 1 / 5;
var BRANCHT = T * 1.5;
var ROOTMAXLENGTH = 40 * 1;
ROOTMAXWIDTH = 10 * 1;
var MINWIDTH = 0.1, MINLENGTH = MINWIDTH;
var LENGTHDECAYSTART = 0.9,
  LENGTHDECAYEND = 0.8;
WIDTHDECAYSTART = 0.9, WIDTHDECAYEND = 0.3;
var MAXEXTANGLE = 3.14 / 12;
var MAXBRANCHES = 2;
var MINBRANCHANGLE = 3.14 / 8,
  MAXBRANCHANGLE = 3.14 / 3;
var MINBRANCHRLP = 0.5,
  MAXBRANCHRLP = 0.8;
var MAXDEPTH = 10;
var MINFRUITDEPTH = 3,
  FRUITPROB = 0.2,
  FRUITMAXLENGTH = 3,
  FRUITMAXWIDTH = 6,
  FRUITGROWTHT = GROWTHT / 5;
var INITWAITT = 0.75;

var canvasDOMElement;

var deltaT;
var nFruits;

var DENSITY = 1, K_PULL = 0.05, PULLMULT = 1;
var pullAngle = -3.1416/2;
var k_pull = K_PULL;
var startedYet = false;


var pushedPullAngles = [];

function myPush() {
  pushedPullAngles.push(pullAngle);
  push();
}

function myPop() {
  pullAngle = pushedPullAngles.pop();
  pop();
}

function myRotate(angle) {
  pullAngle -= angle;
  rotate(angle);
}

class Tree {
  constructor(parent, relLongPos, relAngle, maxLength, maxWidth, isFruit) {
    this.parent = parent;
    this.depth = parent.depth + 1;
    this.relLongPos = relLongPos;
    this.relAngle = relAngle;
    this.pulledAngle = 0;
    if (isFruit) {
      this.maxLength = FRUITMAXLENGTH;
      this.maxWidth = FRUITMAXWIDTH;
      this.growthT = FRUITGROWTHT;
    } else {
      this.maxLength = maxLength;
      this.maxWidth = max(maxWidth, MINWIDTH);
      this.growthT = GROWTHT;
    }
    this.lengthDecay = (this.depth - 1) / (MAXDEPTH - 1) * (LENGTHDECAYEND - LENGTHDECAYSTART) + LENGTHDECAYSTART;
    this.widthDecay = (this.depth - 1) / (MAXDEPTH - 1) * (WIDTHDECAYEND - WIDTHDECAYSTART) + WIDTHDECAYSTART;
    this.isFruit = isFruit;
    this.age = 0
    this.length = MINLENGTH;
    this.width = MINWIDTH;
    this.children = [];
    this.hasExtension = false;
    this.nBranches = 0;
  }
  growAndDraw() {
    // *** grow
    // grow length and width
    let lengthRate = (this.maxLength - this.length) / this.growthT;
    this.length = this.length + lengthRate * deltaT;
    let widthRate = (this.maxWidth - this.width) / this.growthT;
    this.width = this.width + widthRate * deltaT;
    // *** pull
    let k_0 = this.width;
    let K = k_0 + k_pull;
    let equilibAngle = (k_0 * 0 + k_pull * pullAngle) / K;
    let I = DENSITY * Math.pow(this.width, 2) * Math.pow(this.length, 3);
    let pullT = Math.sqrt(I / K);
    let pullRate = (equilibAngle - this.pulledAngle) / pullT;
    this.pulledAngle = this.pulledAngle + pullRate * deltaT;
    myRotate(this.pulledAngle);
    // *** can extend or branch?
    if (!this.isFruit && this.depth < MAXDEPTH) {
      // extend?
      if (!this.hasExtension) {
        let extP = deltaT / EXTT;
        if (Math.random() < extP) {
          this.hasExtension = true;
          let relAngle = MAXEXTANGLE * (Math.random() * 2 - 1);
          let extension = new Tree(this, 1, relAngle, this.lengthDecay * this.maxLength, this.widthDecay * this.maxWidth, false);
          this.children.push(extension);
        }
      }
      // branch?
      if (this.depth > 1 && this.nBranches < MAXBRANCHES) {
        let branchP = deltaT / BRANCHT;
        if (Math.random() < branchP) {
          this.nBranches += 1;
          let relLongPos = (MAXBRANCHRLP - MINBRANCHRLP) * Math.random() + MINBRANCHRLP;
          let relAngle = (MAXBRANCHANGLE - MINBRANCHANGLE) * Math.random() + MINBRANCHANGLE;
          if (Math.random() < 0.5)
            relAngle = -relAngle;
          let fruitChild = (this.depth >= MINFRUITDEPTH && Math.random() < FRUITPROB);
          let branch = new Tree(this, relLongPos, relAngle, this.lengthDecay * this.maxLength, this.widthDecay * this.maxWidth, fruitChild);
          if (fruitChild)
            nFruits += 1;
          this.children.push(branch);
        }
      }
    }
    // *** draw
    if (this.isFruit) {
      noStroke();
      fill('red');
      circle(this.length, 0, this.width);
    } else {
      stroke('black')
      strokeWeight(this.width);
      line(0, 0, this.length, 0);
    }
    // *** grow and draw children
    let child;
    for (child of this.children) {
      myPush()
      // translate to child's position along self
      let relLatPos;
      if (child.relLongPos == 1)
        relLatPos = 0;
      else
        relLatPos = Math.sign(child.relAngle) * this.width/4;
      translate(this.length * child.relLongPos, relLatPos);
      // rotate to child's orientation
      myRotate(child.relAngle)
      child.growAndDraw();
      myPop();
    }
  }
}



var theGround = {
  angle: 0,
  depth: 0
};
var theTree;
var waitingToRestart = false;

function newTree () {
  theTree = new Tree(theGround, 0, -PI / 2, ROOTMAXLENGTH, ROOTMAXWIDTH, false);
  nFruits = 0;
  loop();
}

function setup() {
  let renderer = createCanvas(500, 300);
  canvasDOMElement = renderer.elt;
  newTree();
}

function mouseAtBase() {
  return Math.sqrt((mouseX - width/2) ** 2 + (mouseY - height) ** 2) < 30;
}

/*
// based on https://www.javascripttutorial.net/dom/css/check-if-an-element-is-visible-in-the-viewport/
function isOutsideViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top < -rect.height ||
        rect.left < -rect.width ||
        rect.top > window.innerHeight ||
      rect.top > document.documentElement.clientHeight ||
        rect.right > window.innerWidth ||
      rect.right > document.documentElement.clientWidth
    );
}

function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

*/

function draw() {
	
  //if (!isInViewport(canvasDOMElement))
  //  return;
  
  deltaT = deltaTime / 1000;
  deltaT = min(deltaT, 0.1);
  
  let baseX = width / 2;
  let baseY = height;
  
  
  
  background(220);
  strokeWeight(1)
  
  //const rect = window.frameElement.getBoundingClientRect()
  //text(rect.top.toString() + ', ' + rect.left.toString() + ', ' + rect.bottom.toString() + ', ' + rect.right.toString(), 10, 20);
  
  translate(baseX, baseY); 
  myPush();
  myRotate(theTree.relAngle);
  theTree.growAndDraw();
  myPop();
  
  if (!startedYet && millis() / 1000 > INITWAITT)
	  noLoop(); // wait for first click
}

function mouseClicked() {
  if (!startedYet)
  {
    startedYet = true;
	loop();
  }
  else
    newTree();
  return false;
}


