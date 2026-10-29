#include <QApplication>
#include <QLabel>
#include <QString>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    QLabel* label = new QLabel();
    QString msg = QString("Hello, Qt!");
    label->setText(msg);
    label->show();
    return app.exec();
}