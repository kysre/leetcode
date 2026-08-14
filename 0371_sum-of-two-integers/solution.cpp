class Solution
{
public:
    int getSum(int a, int b)
    {
        unsigned int XOR = a ^ b;
        unsigned int carry_in = ((unsigned int)(a & b)) << 1;
        unsigned int carry_out = 1;
        while (carry_in != 0)
        {
            carry_out = ((unsigned int)(XOR & carry_in)) << 1;
            XOR = XOR ^ carry_in;
            carry_in = carry_out;
        }
        return XOR;
    }
};