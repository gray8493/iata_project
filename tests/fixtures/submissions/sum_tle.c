#include <stdio.h>

/* Bai nop treo: vong lap vo han, dung de kiem tra TLE. */
int main(void) {
    volatile long long i = 0;
    while (1) {
        i++;
    }
    return 0;
}
