import { Component, OnInit, AfterViewInit } from '@angular/core';
import { Food } from '../game-engine/food';
import { outsideGrid } from '../game-engine/gameboard-grid.util';
import { Snake } from '../game-engine/snake';
import { HttpClient } from '@angular/common/http';

  
@Component({
  selector: 'app-game-board',
  templateUrl: './game-board.component.html',
  styleUrls: ['./game-board.component.scss']
})
export class GameBoardComponent implements OnInit, AfterViewInit {

  lastRenderTime = 0
  showScore = false;
  gameOver = false;
  gameBoard: any;
  SNAKE_SPEED = 1;
  scores: any;
  snake = new Snake();
  food = new Food(this.snake);
  playerName = "";
  Object = Object;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.snake.listenToInputs();
  }

  ngAfterViewInit(){
    this.gameBoard = document.querySelector('.game-board');
    window.requestAnimationFrame(this.start.bind(this));
  }


  start(currentTime: any) {
    if(this.gameOver) return console.log('Game Over');

    window.requestAnimationFrame(this.start.bind(this));
    const secondsSinceLastRender = (currentTime - this.lastRenderTime) / 1000;
    if (secondsSinceLastRender < 1 / this.snakeSpeed) return;
    this.lastRenderTime = currentTime;
    this.update();
    this.draw();
  }

  saveScore() {
    let link = 'http://127.0.0.1:8077/?&playerName='+ this.playerName +'&score=' + this.food.currentScore;
    this.http.post<any>(link, {}).subscribe();
  }
  
  showScores() {
    this.http.get<any>('http://localho.st:8077/').subscribe(data => {
      this.scores = data;
      this.showScore = true;
    }); 
  }

  hideScores() {
    this.showScore = false;
  }

  get snakeSpeed() {
    const score = this.food.currentScore;
    if(score < 10) return 4;
    if(score > 10 &&  score < 15 ) return 5;
    if(score > 15 && score < 20 ) return 6;
    return 7;
  }
  
  update() {
    this.snake.update();
    this.food.update();
    this.checkDeath();
  }

  draw() {
    this.gameBoard.innerHTML = '';
    this.snake.draw(this.gameBoard);
    this.food.draw(this.gameBoard);
  }

  checkDeath() {
    this.gameOver = outsideGrid(this.snake.getSnakeHead()) || this.snake.snakeIntersection();
    if(!this.gameOver) return;
    this.gameBoard.classList.add("blur");
  }

  restart() {
    window.location.reload();
  }

}
