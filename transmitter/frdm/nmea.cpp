#include "nmea.h"

void get_line(Serial *s, char *buffer, int buflen)
{
    char *end = buffer + buflen - 1; /* Allow space for null terminator */
    char *dst = buffer;
    char c = s->getc();
    do {
        *dst++ = c;
    } while ((c = s->getc()) != '\n' && c && dst < end);
    *dst = '\0';
//    pc.printf("Read %d characters: %s\r\n", (dst - buffer), buffer);
}

bool StartsWith(const char *a, const char *b)
{
   if(strncmp(a, b, strlen(b)) == 0) return 1;
   return 0;
}

void get_nmea(Serial *s, char *buffer, int buflen)
{
    do {
        get_line(s, buffer, buflen);
    } while (!StartsWith(buffer, "$GPRMC"));
}

struct NMEA_data empty_nmea()
{
    struct NMEA_data ret = { };
    return ret;
}

struct NMEA_data parse_line(char *str)
{
    char line_begin[] = "$GPRMC,";
    if (!StartsWith(str, line_begin))
        return empty_nmea();
    // Else, continue to parse the line
    char* str_ptr = line_begin + strlen(line_begin);
    struct NMEA_data nmea;
    
    // Now parse the rest of the line
//    pc.printf("%s\r\n", str);
    sscanf(str, "$GPRMC,%2d%2d%2d.000,%c,%2d%lf,%c,%3d%lf,%c,%lf,%lf,%2d%2d%2d", 
        &nmea.hours, &nmea.minutes, &nmea.seconds, &nmea.lock_flag, 
        // latitude
        &nmea.latitude, &nmea.latitude_minutes, &nmea.latitude_direction,
        // longitude
        &nmea.longitude, &nmea.longitude_minutes, &nmea.longitude_direction,
        // bearing
        &nmea.speed, &nmea.tracking_angle,
        // date
        &nmea.day, &nmea.month, &nmea.year );
        
    if (nmea.lock_flag != 'A') {
        // No lock -- get rid of garbage data (everything except time)
        nmea.latitude = 0;
        nmea.latitude_minutes = 0.00;
        nmea.latitude_direction = 'N';
        
        nmea.longitude = 0;
        nmea.longitude_minutes = 0.00;
        nmea.longitude_direction = 'E';
        
        nmea.speed = 0.00;
        nmea.tracking_angle = 0.00;
        
        nmea.day = 0;
        nmea.month = 0;
        nmea.year = 0;
    }

    return nmea;
}