// Copyright (C) 2018, Vladimir Shapranov 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

#ifndef PyDecoderPlugin_H
#define PyDecoderPlugin_H

// Python first! Having Qt before it breaks the build!
#include <boost/python.hpp>
#include <QObject>
#include "plugininterface.h"



class PyDecoderPlugin : public QObject, QDLTPluginInterface, QDLTPluginDecoderInterface
{
    Q_OBJECT
    Q_INTERFACES(QDLTPluginInterface)
    Q_INTERFACES(QDLTPluginDecoderInterface)
#ifdef QT5
    Q_PLUGIN_METADATA(IID "org.genivi.DLT.PythonDecoderPlugin")
#endif
    boost::python::object pyDelegate;

public:
    PyDecoderPlugin();
    ~PyDecoderPlugin();

    /* QDLTPluginInterface interface */
    QString name();
    QString pluginVersion();
    QString pluginInterfaceVersion();
    QString description();
    QString error();
    bool loadConfig(QString filename);
    bool saveConfig(QString filename);
    QStringList infoConfig();

    /* QDltPluginDecoderInterface */
    bool isMsg(QDltMsg &msg, int triggeredByUser);
    bool decodeMsg(QDltMsg &msg, int triggeredByUser);

private:
    QString errorText;
};

#endif // PyDecoderPlugin_H
