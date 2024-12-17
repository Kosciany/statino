#include <LiquidCrystal.h>

#define RS 8
#define EN 9
#define D4 4
#define D5 5
#define D6 6
#define D7 7
#define LCD_REST_TIME_MS 125
#define CHAR_IN_LINES 16
#define BUFF_SIZE 50
#define BAUD_RATE 9600
#define LINE_TERMINATOR ';'

struct PCStats
{
  int CPU;
  int RAM;
  int RAMd;
  int GPU;
  int VRAM;
  int VRAMd;
};

struct PCStats pcstats;

String serial_input_buff;
char input_buff[BUFF_SIZE];
char first_line[CHAR_IN_LINES + 1];
char second_line[CHAR_IN_LINES + 1];
LiquidCrystal lcd(RS, EN, D4, D5, D6, D7);

void setup()
{
  lcd.begin(16, 2);
  Serial.begin(BAUD_RATE);
}

void loop()
{

  if (Serial.available() > 0)
  {
    serial_input_buff = Serial.readStringUntil(LINE_TERMINATOR);
    serial_input_buff.toCharArray(input_buff, BUFF_SIZE);

    // Arduino does not have support for float numbers, 
    // so we need to split the number in two parts
    sscanf(input_buff, "%d,%d,%d.%d,%d.%d;",
           &pcstats.CPU, &pcstats.GPU, &pcstats.RAM, &pcstats.RAMd, 
           &pcstats.VRAM, &pcstats.VRAMd);

    sprintf(first_line, "CPU %2d%% RAM %2d.%1d", 
            pcstats.CPU, pcstats.RAM, pcstats.RAMd);

    sprintf(second_line, "GPU %2d%% VRAM %1d.%1d", 
            pcstats.GPU, pcstats.VRAM, pcstats.VRAMd);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(first_line);
    lcd.setCursor(0, 1);
    lcd.print(second_line);
  }
}
