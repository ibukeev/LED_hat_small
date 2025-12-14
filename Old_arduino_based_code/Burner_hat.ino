

#include <Adafruit_GFX.h>
#include <Adafruit_NeoMatrix.h>
#include <Adafruit_NeoPixel.h>


#ifndef PSTR
#define PSTR // Make Arduino Due happy
#endif

#define DEBUG 1
// Enable serial output
#define SERIAL_OUT  1
#define INIT_MSG  "Strip is set to 32-bit type (RGBW)"

//LED CONFIG
#define PIN 3
#define NUMPIXELS  240
#define BRIGHTNESS  240 // set max brightness
#define MATRIX_WIDTH 19
#define MATRIX_HEIGHT 9
#define WAIT 100

//const int matrix_width = 19;
//const int matrix_height = 9;


//WAVE CONFIG
#define W_COUNT 1                 //Number of simultaneous waves
#define W_SPEED_FACTOR 4          //Higher number, higher speed
#define W_WIDTH_FACTOR 1          //Higher number, smaller waves
#define W_COLOR_WEIGHT_PRESET 2   //What color weighting to choose
#define W_RANDOM_SEED 11          //Change this seed for a different pattern. If you read from an analog input here you can get a different pattern everytime.


//Initializing matrix
Adafruit_NeoMatrix matrix = Adafruit_NeoMatrix(MATRIX_WIDTH, MATRIX_HEIGHT, PIN,
                            NEO_MATRIX_TOP     + NEO_MATRIX_LEFT +
                            NEO_MATRIX_COLUMNS + NEO_MATRIX_ZIGZAG,
                            NEO_RGB            + NEO_KHZ800);


//defining various coloring schemes
const uint16_t colors_psy[] = {
  matrix.Color(0, 148, 85), 
  matrix.Color(113, 0, 89)
};

const uint16_t colors_gradient_1[] = {
  matrix.Color(236, 21, 27), 
  matrix.Color(255, 242, 82), 
  matrix.Color(111, 14, 155), 
  matrix.Color(13, 238, 72)
};

const uint16_t colors_gradient_2[] = {
  matrix.Color(32, 27, 207), 
  matrix.Color(212, 55, 198), 
  matrix.Color(75, 218, 156), 
  matrix.Color(249, 88, 138), 
  matrix.Color(0, 131, 120)
};


byte allowedcolors[5][3] ={
  { 17, 177, 13 },    //Greenish
  { 148, 242, 5 },    //Greenish
  { 25, 173, 121},    //Turquoise
  { 250, 77, 127 },   //Pink
  { 171, 101, 221 },  //Purple
};


//Colorweighing allows to give some colors more weight so it is more likely to be choosen for a wave.
//The second dimension of this array must match the first dimension of the allowedcolors array
//Here are 3 presets.
byte colorweighting[3][5] = {
  {10, 10, 10, 10, 10},   //Weighting equal (every color is equally likely)
  {2, 2, 2, 6, 6},        //Weighting reddish (red colors are more likely)
  {6, 6, 6, 2, 2}         //Weighting greenish (green colors are more likely)
};


//Setting up the modes changing
int LED_Mode = 0;
int LED_Mode_prev = 0;
int state = 0;
int num_modes = 2;


//Function to get the color for a wave based on the weighting.
//Paramter weighting: First index of colorweighting array. Basically what preset to choose.
byte getWeightedColor(byte weighting) {
  byte sumOfWeights = 0;

  for(byte i = 0; i < sizeof colorweighting[0]; i++) {
    sumOfWeights += colorweighting[weighting][i];
  }

  byte randomweight = random(0, sumOfWeights);
  
  for(byte i = 0; i < sizeof colorweighting[0]; i++) {
    if(randomweight < colorweighting[weighting][i]) {
      return i;
    }
    
    randomweight -= colorweighting[weighting][i];
  }
}


class BorealisWave {
   private:
   //int ttl = random(500, 1501);
   int ttl = random(30, 300);
   byte basecolor = getWeightedColor(W_COLOR_WEIGHT_PRESET);
   float basealpha = random(50, 101) / (float)100;
   int age = 0;
   //int width = random(MATRIX_WIDTH / 2, MATRIX_WIDTH/ W_WIDTH_FACTOR);
   int width = MATRIX_WIDTH +1;
   float center = random(101) / (float)100 * MATRIX_WIDTH;
   bool goingleft = random(0, 2) == 0;
   //float speed = random(10, 30) / (float)100 * W_SPEED_FACTOR;
   float speed = 0.0;
   bool alive = true;



   public:
    int * getColorForLED(int ledIndex) {
          /*Serial.println("Center is");
          Serial.println(center);
          Serial.println("Half width is");
          Serial.println(width / 2);*/

      //if (((center < ledIndex) && ((ledIndex - center > width / 2) || (center - ledIndex + MATRIX_WIDTH > width / 2))) || ((center >= ledIndex) && ((center - ledIndex > width / 2) || ( ledIndex + MATRIX_WIDTH - center > width / 2)))) {
      //if( not(ledIndex < center - width / 2 || ledIndex > center + width / 2 ))
      if( (abs(center - ledIndex) <= width / 2 ) || (abs(center - ledIndex) >= MATRIX_WIDTH - width / 2 )  ) 
      {
        static int color_wave[3];
        //Offset of this led from center of wave
        //The further away from the center, the dimmer the LED
        int offset = min(min(abs(ledIndex - center), abs(ledIndex + MATRIX_WIDTH - center)),abs(ledIndex - MATRIX_WIDTH - center)) ;
        //float offsetFactor = (float)offset / (width / 2);
        float offsetFactor = (float)offset / width /2;

        //The age of the wave determines it brightness.
        //At half its maximum age it will be the brightest.
        float ageFactor = 1;        
        if((float)age / ttl < 0.5) {
          ageFactor = (float)age / (ttl / 2);
        } else {
          ageFactor = (float)(ttl - age) / ((float)ttl * 0.5);
        }

        //ageFactor = 1.0;
        //offsetFactor = 0.0;
        /*
        Serial.println("Base color is");
        Serial.println(allowedcolors[basecolor][0]);
        Serial.println("1 - offest factor is ");
        Serial.println((1 - offsetFactor));
        Serial.println("ageFactor");
        Serial.println(ageFactor);
        Serial.println("basealpha");
        Serial.println(basealpha);
        Serial.println("TTL");
        Serial.println(ttl); */

        
        //Calculate color based on above factors and basealpha value
        color_wave[0] = allowedcolors[basecolor][0] * (1 - offsetFactor) * ageFactor * basealpha;
        color_wave[1] = allowedcolors[basecolor][1] * (1 - offsetFactor) * ageFactor * basealpha;
        color_wave[2] = allowedcolors[basecolor][2] * (1 - offsetFactor) * ageFactor * basealpha;

        /*Serial.println("Color 0");
        Serial.println(color_wave[0]);
        Serial.println("Color 1");
        Serial.println(color_wave[1]);
        Serial.println("Color 2");
        Serial.println(color_wave[2]);*/


        return color_wave;
        
        }

      else 
      {
        //if( not (ledIndex < center - width / 2) && not (ledIndex > center + width / 2)) {
        
        //Position out of range of this wave
          //Serial.println("Position is out of range");

        return NULL;
      }
      };


    //Change position and age of wave
    //Determine if its sill "alive"
    void update() {
      if(goingleft) {
        center -= speed;
        if(center<0) {center = MATRIX_WIDTH;};
      } else {
        center += speed;
        if(center>MATRIX_WIDTH) {center = 0;};
      }

      age++;

      if(age > ttl) {
        alive = false;
      } else {
        if(goingleft) {
          if(center + width / 2 < 0) {
            alive = false;
          }
        } else {
          if(center - width / 2 > MATRIX_WIDTH) {
            alive = false;
          }
        }
      }
    };
      
      bool stillAlive() {
      return alive;
      };

  };


BorealisWave* waves[W_COUNT];

void setup() {
  // put your setup code here, to run once:
  randomSeed(W_RANDOM_SEED);

#ifdef SERIAL_OUT
  // initialize serial communication:
  while (!Serial);  // for Leonardo/Micro/Zero
  Serial.begin(9600);
  Serial.println(INIT_MSG);
#endif

  for(int i = 0; i < W_COUNT; i++) {
    waves[i] = new BorealisWave();
  }



  matrix.begin();
  //matrix.setTextWrap(false);
  matrix.setBrightness(BRIGHTNESS);
  //matrix.setTextColor(colors[0]);
  matrix.fillScreen(matrix.Color(0, 0, 0));


}



void loop() {
  // put your main code here, to run repeatedly:
  switch (LED_Mode) {
    case 0:
    // blackout(); break;
    aurora(); break;
    case 1: 
    bars_2(); break;
    case 2:
     ukrainian_flag(); break;
    case 3:
    bars_1();break;
    case 4: snake();;break;
    default:
    blackout();
    }
}




void aurora()
{
  /*Serial.println("Wave color 1 is ");
  Serial.println(*waves[0]->getColorForLED(8));
  Serial.println("Wave color 2 is ");
  Serial.println(*(waves[0]->getColorForLED(8)+1));
  Serial.println("_____");*/


  
  

  for(int i = 0; i < MATRIX_WIDTH; i++) {

    
    uint16_t mixed_color = matrix.Color(0,0,0);

    for(int  j = 0; j < W_COUNT; j++) {
      Serial.println(j);
      int* ptr = waves[j]->getColorForLED(i); 
      if(ptr) {
      
      mixed_color += matrix.Color(*(ptr+0),*(ptr+1),*(ptr+2));
      }

      
      }
   
    //fill_vertical(i, matrix.Color(*(waves[0]->getColorForLED(i)+0), *(waves[0]->getColorForLED(i)+1), *(waves[0]->getColorForLED(i)+2)) + matrix.Color(*(waves[1]->getColorForLED(i)+0), *(waves[1]->getColorForLED(i)+1), *(waves[1]->getColorForLED(i)+2)));
    //fill_vertical(i, matrix.Color(*(waves[0]->getColorForLED(i)+0), *(waves[0]->getColorForLED(i)+1), *(waves[0]->getColorForLED(i)+2)));
    fill_vertical(i, mixed_color);
  }
  matrix.show();
  checkButton(10);

  
  //matrix.fillScreen(matrix.Color(*(waves[0]->getColorForLED(8)+0), *(waves[0]->getColorForLED(8)+1), *(waves[0]->getColorForLED(8)+2)));
  //matrix.show();

  for(int i = 0; i < W_COUNT; i++) {
    
    waves[i] -> update();

      if(!(waves[i] -> stillAlive())) {
      //If a wave dies, remove it from memory and spawn a new one
      delete waves[i];
      waves[i] = new BorealisWave();
    }

  }
  
  
  
  
  //checkButton(1000);
  }


//Various graphic patterns

void blackout() {
  matrix.fillScreen(matrix.Color(0, 0, 0));
  matrix.show();
  checkButton(300);
  }



void fill_vertical(int line, uint16_t color_mix)
{
  for (int k = 0 ; k < matrix.height();k++)
  {
    matrix.drawPixel(line, k, color_mix);
    }
    return;
  
  
  
  }


void bars_2()
{
  int color_LED = 0;
  uint16_t row = 0;

  for (uint16_t k = 0; k < matrix.height() * 2 + 1; k++)
  {
    if (k > matrix.height() - 1) {
      row = 2 * matrix.height() - k;
    }
    else {
      row = k;
    }
    matrix.fillScreen(colors_psy[1]);
    for (uint16_t column = 0; column < matrix.width(); column++)
    {
      matrix.drawPixel(column, row, colors_psy[0]);
      matrix.drawPixel(column, row + 1, colors_psy[0]);

    }
    if (checkButton(WAIT*4) > 0) {return;}
    //delay(wait * 4);
    matrix.show();
  }
}


int checkButton(uint16_t wait_sec)
{
  int keyVal = analogRead(A0);

  for (uint16_t i = 0; i < wait_sec; i+=10)
  {
    delay(10);
      if ((keyVal > 50) and (state < 1))
  {
    //Serial.println(keyVal);
    //Serial.println(LED_Mode);
    if (LED_Mode > num_modes + 1)
    {
      LED_Mode = 0;
    }
    else {
      LED_Mode = LED_Mode + 1;
    }
    Serial.println(keyVal);
    Serial.println(LED_Mode);

    state = keyVal;
    return 1;

  }
  else if ((keyVal < 50) and (state > 0))
  {
    state = 0;
  }    
    }

  return 0;


}


void snake()
{
  matrix.fillScreen(matrix.Color(0, 0, 0));
  for (uint16_t row = 0; row < 9; row++) {
    for (uint16_t column = 0; column < 20; column++) {
      if (checkButton(WAIT) > 0) {return;}
      matrix.drawPixel(column, row, colors_psy[LED_Mode]/*matrix.Color(255, 0, 0)*/);
      matrix.show();
    }
  }
}


void ukrainian_flag()
{
  //matrix.fillScreen(matrix.Color(255, 255, 255));
  //matrix.show();
  //delay(1000);


  for (uint16_t row = 0; row < 9; row++) {
    for (uint16_t column = 0; column < 20; column++)
    {
      if (row < 4)
      {
        matrix.drawPixel(column, row, matrix.Color(255, 255, 0));
      }
      else {
        matrix.drawPixel(column, row, matrix.Color(0, 0, 255));
      }
    }
  }
  if (checkButton(1000) > 0) {return;}
  matrix.show();
  

  //matrix.fillScreen(matrix.Color(0, 0, 255));

}



void bars_1()
{
  matrix.fillScreen(matrix.Color(100, 100, 100));

  int color_LED = 0 ;
  for (uint16_t row = 0; row < matrix.height(); row++)
  {
    for (uint16_t column = 0; column < matrix.width(); column++)
    {
      color_LED = (int)row / 2;
      if (row == 8) {
        color_LED = 3;
      };

      matrix.drawPixel(column, row, colors_gradient_1[color_LED]);

    }
    matrix.show();
    if (checkButton(WAIT * 4) > 0) {return;}
  }
}



void text()
{

  int x    = matrix.width();
  int pass = 0;
  //int len = 3;


  //matrix.setTextColor(colors[1]);
  matrix.setTextWrap(false);

  matrix.fillScreen(0);
  matrix.setCursor(x, 0);
  matrix.print(F("Arduino"));
  if (--x < -36) {
    x = matrix.width();
    if (++pass >= 3) pass = 0;
    //matrix.setTextColor(colors[pass]);
  }
  matrix.show();
  delay(100);

}
