// Copyright (C) 2018, Vladimir Shapranov 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

#include <Python.h>
#include "pydecoderplugin.h"
#include <QtGui>

using namespace boost::python;

dict msgToDict(const QDltMsg& msg){
    // Ideally we should pass some object with getters for lazy retrieving of the stuff,
    // but so far let it be just dict for simplicity
    dict ret;
    ret["app"] = str(msg.getApid().toStdString());
    ret["ctx"] = str(msg.getCtid().toStdString());
    ret["ts"] = msg.getTimestamp();
    QByteArray pl = msg.getPayload();
    // Should work, but gives some funny behaviour instead
    // ret["pl"] = handle<>(PyMemoryView_FromMemory(pl.data(), pl.length(), PyBUF_READ));
    // Works, but should not (pl is destroyed)
    // ret["pl"] = handle<>(PyMemoryView_FromMemory((char*)pl.constData(), pl.length(), PyBUF_READ));

    // Safe but inefficient since it copies the buffer
    ret["pl"] = handle<>(PyBytes_FromStringAndSize(pl.data(), pl.length()));

    return ret;
}

class ScopedGil{
    PyGILState_STATE gil;
public:
    ScopedGil(){
        gil = PyGILState_Ensure();
    }
    ~ScopedGil(){
        PyGILState_Release(gil);
    }
};

PyDecoderPlugin::PyDecoderPlugin()
{
    Py_Initialize();
    object main_module = import("__main__");
    dict main_namespace = extract<dict>(main_module.attr("__dict__"));
    main_namespace["testvar"] = "test";

    object ignored = exec(
        "import os.path\n"
        "exec(open(os.path.expanduser('~/.config/pydltdecoder.py')).read())",
        main_namespace);
    pyDelegate = main_namespace["decoder"];
}

PyDecoderPlugin::~PyDecoderPlugin()
{

}

QString PyDecoderPlugin::name()
{
    return QString("Python Decoder Plugin");
}

QString PyDecoderPlugin::pluginVersion(){
    return "0.0.1";
}

QString PyDecoderPlugin::pluginInterfaceVersion(){
    return PLUGIN_INTERFACE_VERSION;
}

QString PyDecoderPlugin::description()
{
    return QString();
}

QString PyDecoderPlugin::error()
{
    return QString();
}

bool PyDecoderPlugin::loadConfig(QString filename )
{
    ScopedGil gil;
    pyDelegate.attr("load_config")(filename.toStdString());
    return true;
}

bool PyDecoderPlugin::saveConfig(QString /* filename */)
{
    return true;
}

QStringList PyDecoderPlugin::infoConfig()
{
    return QStringList();
}

bool PyDecoderPlugin::isMsg(QDltMsg & msg, int triggeredByUser)
{
    Q_UNUSED(msg);
    Q_UNUSED(triggeredByUser);
    if (msg.getMode() != QDltMsg::DltModeVerbose || msg.sizeArguments() == 0){
        return false;
    }

    ScopedGil gil;
    return extract<bool>(pyDelegate.attr("check_message")(msgToDict(msg)));
}

bool PyDecoderPlugin::decodeMsg(QDltMsg &msg, int triggeredByUser)
{
    Q_UNUSED(msg);
    Q_UNUSED(triggeredByUser);
    ScopedGil gil;

    tuple py_ret = extract<tuple>(pyDelegate.attr("decode_message")(msgToDict(msg)));

    bool success = extract<bool>(py_ret[0]);
    if (success)
    {
        std::string msg_decoded = extract<std::string>(py_ret[1]);
        msg.clearArguments();
        QDltArgument argument;
        argument.setTypeInfo(QDltArgument::DltTypeInfoStrg);
        argument.setEndianness(msg.getEndianness());
        argument.setOffsetPayload(0);
        argument.setData(QByteArray(msg_decoded.c_str()));
        msg.addArgument(argument);
    }

    return success;
}

#ifndef QT5
Q_EXPORT_PLUGIN2(pythondecoderplugin, PyDecoderPlugin);
#endif

