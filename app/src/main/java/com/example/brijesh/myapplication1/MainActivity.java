package com.example.brijesh.myapplication1;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity
{

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toast.makeText(this,"Brijesh",Toast.LENGTH_LONG).show();
        int res=fun();
        Toast.makeText(this,res,Toast.LENGTH_LONG).show();
    }
    private int fun()
    {
        int i=5;
        int ii=i+90;
       return ii;
    }
}
