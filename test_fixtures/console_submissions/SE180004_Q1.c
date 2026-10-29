#include <stdio.h>

int main() {
    int a, b;
    if (scanf("%d %d", &a, &b) == 2) {
        while (1) {
            // Vòng lặp vô tận gây TLE
            a++;
        }
        printf("%d\n", a + b);
    }
    return 0;
}
