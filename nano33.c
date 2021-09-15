#include "mbed.h"   // For changing PWM frequency

#define PIN_PWM      D9   // Output PWM
#define PIN_SYNC     D10  // For scope trigger
#define PIN_IN       A0   // For analog read

#define CAPTURE_SIZE 1500
#define BAUD_RATE    115200


// Start, Stop frequency
double f_start=100e3; 
double f_end  =1e6;

// Buffer
uint16_t input[CAPTURE_SIZE+2];

// 
int delimeter_length=4;
uint8_t delimiter[]={0xde, 0xad, 0xbe, 0xef};

// Init PWM pin
mbed::PwmOut pwmPin(digitalPinToPinName(PIN_PWM));

int    dutycycle=50;
double f        =0;


void setup()
{
    pinMode(PIN_PWM,  OUTPUT);
    pinMode(PIN_SYNC, OUTPUT);
    pinMode(PIN_IN,    INPUT);

    Serial.begin(BAUD_RATE);

    // Set ADC resolution to 12-bit 
    analogReadResolution(12);

    // Set PWM frequency and dutycycle
    f=1e4;              // Dummy freq
    dutycycle=50;
    pwmPin.period(1.0/f);
    pwmPin.write(dutycycle/100.0);
}

void loop()
{
    collect_sample();
    send_sample();
}

void collect_sample()
{
    // Reset the index for the input buffer
    int i=0;

    // Set sync signal
    digitalWrite(PIN_SYNC, HIGH);

    // Loop through CAPTURE_SIZE samples and frequency sweep steps
    while(i<CAPTURE_SIZE)
    {
        input[i]=analogRead(PIN_IN);
        // Serial.println(input[i]);
        
        // Logarithmic
        int f=pow(10, (log10(f_end-f_start)*((i*1.0)/(CAPTURE_SIZE-1))))+f_start;
    
        pwmPin.period(1.0/f);
        pwmPin.write(dutycycle/100.0);
    
        //delayMicroseconds(1000);
        i++;
    }

    // Reset sync signal
    digitalWrite(PIN_SYNC, LOW);
}

void send_sample()
{
    /*
    // Print the delimiter
    for(int k = 0; k < delimeter_length; k++)
    {
        Serial.write(delimiter[k]);
    }
    */
    Serial.write(delimiter, sizeof(delimiter));

    // Channel byte (one at the end of each channel's transmission)
    input[CAPTURE_SIZE]  =0;
    // Frame completion byte (only after all channels sent)
    input[CAPTURE_SIZE+1]=1;


    /*
    // Print the data
    for(int k = 0; k < CAPTURE_SIZE; k++)
    {
        Serial.write((uint8_t)(input[k]>>8));
        Serial.write((uint8_t)(input[k]));
    }
    */
    
    Serial.write((uint8_t *)input, sizeof(input));
}