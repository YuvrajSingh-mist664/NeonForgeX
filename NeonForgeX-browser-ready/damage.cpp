#include <iostream>

int calculateDamage(int attack, int defense)
{
    int damage = attack - defense;

    if(damage < 1)
        damage = 1;

    return damage;
}

int main()
{
    std::cout << calculateDamage(100, 25);
    return 0;
}