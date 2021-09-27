#include "mbed.h"

#define SAMPLES_PER_SECOND  (16000000)
#define PPI_CHANNEL_T4      (7)

// Arduino Nano 33 BLE Digital pin D10 P1.02 (port 1 pin 2)
#define PIN_GPIO_T4         (2)
#define PORT_GPIO_T4        (1)

#define PIN_PWM      D10   // Output PWM
#define PIN_SYNC     D9    // For scope trigger
#define PIN_IN       A0    // For analog read

#define CAPTURE_SIZE 1500
#define BAUD_RATE    115200

// Start, Stop frequency
double f_start=100e3; 
double f_end  =1e6;

// Buffer
uint16_t input[CAPTURE_SIZE+2];
uint16_t tmp_buf[5];

// 
int delimeter_length=4;
uint8_t delimiter[] ={0xde, 0xad, 0xbe, 0xef};

// Init PWM pin
mbed::PwmOut pwmPin(digitalPinToPinName(PIN_PWM));

int    dutycycle=50;
double f        =0;


void setup()
{
    // Pin mode
    pinMode(PIN_SYNC, OUTPUT);
    pinMode(PIN_IN,    INPUT);

    // Baud rate
    Serial.begin(BAUD_RATE);

    // Set ADC resolution to 12-bit 
    analogReadResolution(12);

    // Set PWM Freq
    initTimer4(1e3);
    initGPIOTE();
    initPPI();
}

void loop()
{
    collect_sample();
    send_sample();
}


void initTimer4(int f)
{
    NRF_TIMER4->MODE = TIMER_MODE_MODE_Timer;
    NRF_TIMER4->BITMODE = TIMER_BITMODE_BITMODE_16Bit;
    NRF_TIMER4->SHORTS = TIMER_SHORTS_COMPARE0_CLEAR_Enabled << TIMER_SHORTS_COMPARE0_CLEAR_Pos;
    NRF_TIMER4->PRESCALER = 0;
    // NRF_TIMER4->CC[0] = 16000000 / SAMPLES_PER_SECOND; // Needs prescaler set to 0 (1:1) 16MHz clock
    NRF_TIMER4->CC[0] = 16000000 /(f*2); // Needs prescaler set to 0 (1:1) 16MHz clock
    NRF_TIMER4->TASKS_START = 1;
}

void initGPIOTE()
{
    NRF_GPIOTE->CONFIG[0] = ( GPIOTE_CONFIG_MODE_Task       << GPIOTE_CONFIG_MODE_Pos ) |
                            ( GPIOTE_CONFIG_OUTINIT_Low     << GPIOTE_CONFIG_OUTINIT_Pos ) |
                            ( GPIOTE_CONFIG_POLARITY_Toggle << GPIOTE_CONFIG_POLARITY_Pos ) |
                            ( PORT_GPIO_T4                  << GPIOTE_CONFIG_PORT_Pos ) |
                            ( PIN_GPIO_T4                   << GPIOTE_CONFIG_PSEL_Pos );
}

void initPPI()
{
    // Configure PPI channel with connection between TIMER->EVENTS_COMPARE[0] and GPIOTE->TASKS_OUT[0]
    NRF_PPI->CH[PPI_CHANNEL_T4].EEP = ( uint32_t )&NRF_TIMER4->EVENTS_COMPARE[0];
    NRF_PPI->CH[PPI_CHANNEL_T4].TEP = ( uint32_t )&NRF_GPIOTE->TASKS_OUT[0];

    // Enable PPI channel
    NRF_PPI->CHENSET = ( 1UL << PPI_CHANNEL_T4 );
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
        // if(i>1 && i<(CAPTURE_SIZE-1))
        // {
        //     do
        //     {
        //         input[i]+=analogRead(PIN_IN);
        //     }
        //     while((input[i]-input[i-1])>50);
        // }
        
        while(input[i]< 900)input[i]=analogRead(PIN_IN);
        // while(input[i]>3200)input[i]=analogRead(PIN_IN);

        // if(input[i]<100)
        // {
        //     Serial.println(i);
        //     Serial.println(int(input[i]));    
        // }

        // Serial.println(i, input[i]);
        
        // Logarithmic
        int f=pow(10, (log10(f_end-f_start)*((i*1.0)/(CAPTURE_SIZE-1))))+f_start;
    
        initTimer4(f);
        initGPIOTE();
        initPPI();
    
        // delayMicroseconds(10);
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

    // Channel number (one at the end of each channel's transmission)
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