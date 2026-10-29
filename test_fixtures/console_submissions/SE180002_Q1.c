#include <stdio.h>

int main() {
    int a, b;
    if (scanf("%d %d", &a, &b) == 2) {
        // Lỗi in thừa chuỗi "Result: " khiến testcase bị WA
        printf("Result: %d\n", a + b);
    }
    return 0;
}
