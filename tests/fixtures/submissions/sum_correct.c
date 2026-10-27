#include <stdio.h>

/* Bai nop mau dung: doc 2 so nguyen, in tong. */
int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) {
        return 1;
    }
    printf("%d\n", a + b);
    return 0;
}
