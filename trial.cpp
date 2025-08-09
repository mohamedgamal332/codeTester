   class Circle : public Shape {
   public:
       Circle(double r) : radius(r) {}
       double area() const override {   // Fix: Replace "dou" with "double"
           return 3.14159 * radius * radius;
       }
   private:
       double radius;
   };