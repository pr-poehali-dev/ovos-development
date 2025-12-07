import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import Icon from '@/components/ui/icon';
import { toast } from 'sonner';

const Index = () => {
  const navigate = useNavigate();
  const [nickname, setNickname] = useState('');
  const [amount, setAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nickname.trim() || !amount.trim()) {
      toast.error('Заполните все поля');
      return;
    }

    const amountNum = parseInt(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      toast.error('Введите корректную сумму');
      return;
    }

    setIsLoading(true);
    
    localStorage.setItem('donateRequest', JSON.stringify({
      nickname: nickname.trim(),
      amount: amountNum,
      timestamp: Date.now()
    }));

    setTimeout(() => {
      setIsLoading(false);
      toast.success('Заявка создана! Переходим к оплате...');
      navigate('/payment');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center space-y-2 animate-fade-in">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center shadow-lg">
              <Icon name="Coins" size={40} className="text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-secondary">
            Донат Рубли
          </h1>
          <p className="text-muted-foreground text-lg">
            Пополните игровой баланс на сервере
          </p>
        </div>

        <Card className="shadow-2xl border-2 animate-scale-in">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Оформление заявки</CardTitle>
            <CardDescription className="text-center">
              Введите данные для пополнения донат рублей
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="nickname" className="text-base">
                  Ваш игровой ник
                </Label>
                <div className="relative">
                  <Icon 
                    name="User" 
                    size={20} 
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" 
                  />
                  <Input
                    id="nickname"
                    type="text"
                    placeholder="Введите ник"
                    value={nickname}
                    onChange={(e) => setNickname(e.target.value)}
                    className="pl-10 h-12 text-base"
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount" className="text-base">
                  Количество донат рублей
                </Label>
                <div className="relative">
                  <Icon 
                    name="Wallet" 
                    size={20} 
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" 
                  />
                  <Input
                    id="amount"
                    type="number"
                    placeholder="100"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="pl-10 h-12 text-base"
                    disabled={isLoading}
                    min="1"
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  Минимальная сумма: 100 рублей
                </p>
              </div>

              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold shadow-lg hover:shadow-xl transition-all"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Icon name="Loader2" size={20} className="mr-2 animate-spin" />
                    Обработка...
                  </>
                ) : (
                  <>
                    Перейти к оплате
                    <Icon name="ArrowRight" size={20} className="ml-2" />
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="text-center text-sm text-muted-foreground animate-fade-in">
          <p>После оплаты донат рубли поступят автоматически</p>
          <p className="mt-1 flex items-center justify-center gap-1">
            <Icon name="Shield" size={16} />
            Безопасная система пополнения
          </p>
        </div>
      </div>
    </div>
  );
};

export default Index;
