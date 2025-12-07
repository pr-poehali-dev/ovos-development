import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Icon from '@/components/ui/icon';
import { toast } from 'sonner';

interface DonateRequest {
  nickname: string;
  amount: number;
  timestamp: number;
}

const Payment = () => {
  const navigate = useNavigate();
  const [request, setRequest] = useState<DonateRequest | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const data = localStorage.getItem('donateRequest');
    if (!data) {
      toast.error('Заявка не найдена');
      navigate('/');
      return;
    }
    setRequest(JSON.parse(data));
  }, [navigate]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Скопировано в буфер обмена');
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePaymentConfirm = async () => {
    if (!request) return;
    
    try {
      const response = await fetch('https://functions.poehali.dev/6b9d0b26-9bb4-4506-9276-c04e97feeea5', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'create_request',
          nickname: request.nickname,
          amount: request.amount,
          timestamp: request.timestamp
        })
      });
      
      if (response.ok) {
        toast.success('Заявка отправлена администратору на проверку');
        setTimeout(() => {
          navigate('/');
        }, 2000);
      } else {
        toast.error('Ошибка отправки заявки');
      }
    } catch (error) {
      toast.error('Ошибка соединения');
    }
  };

  if (!request) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl space-y-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4"
        >
          <Icon name="ArrowLeft" size={20} className="mr-2" />
          Назад
        </Button>

        <Card className="shadow-2xl border-2 animate-scale-in">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center shadow-lg">
                <Icon name="CreditCard" size={32} className="text-white" />
              </div>
            </div>
            <CardTitle className="text-3xl">Реквизиты для оплаты</CardTitle>
            <CardDescription className="text-base mt-2">
              Переведите средства по указанным реквизитам
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-blue-50 border-2 border-primary/20 rounded-lg p-6 space-y-4">
              <div className="flex items-center justify-between pb-4 border-b">
                <div>
                  <p className="text-sm text-muted-foreground">Игровой ник</p>
                  <p className="text-xl font-bold text-secondary">{request.nickname}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Сумма к оплате</p>
                  <p className="text-2xl font-bold text-primary">{request.amount} ₽</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-white rounded-lg p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-muted-foreground mb-1">
                        Номер карты
                      </p>
                      <p className="text-lg font-mono font-semibold">
                        1234 5678 9012 3456
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopy('1234567890123456')}
                      className="shrink-0"
                    >
                      <Icon name={copied ? "Check" : "Copy"} size={16} />
                    </Button>
                  </div>
                </div>


              </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3">
              <Icon name="AlertCircle" size={20} className="text-amber-600 shrink-0 mt-0.5" />
              <div className="text-sm text-amber-800">
                <p className="font-semibold mb-1">Важно!</p>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Указывайте точную сумму: {request.amount} ₽</li>
                  <li>В комментарии к платежу укажите ваш ник: {request.nickname}</li>
                  <li>После оплаты нажмите кнопку "Я оплатил"</li>
                </ul>
              </div>
            </div>

            <Button 
              onClick={handlePaymentConfirm}
              className="w-full h-12 text-base font-semibold shadow-lg hover:shadow-xl transition-all"
            >
              <Icon name="CheckCircle" size={20} className="mr-2" />
              Я оплатил
            </Button>
          </CardContent>
        </Card>

        <div className="text-center text-sm text-muted-foreground">
          <p className="flex items-center justify-center gap-1">
            <Icon name="Clock" size={16} />
            Проверка платежа занимает от 5 до 30 минут
          </p>
        </div>
      </div>
    </div>
  );
};

export default Payment;