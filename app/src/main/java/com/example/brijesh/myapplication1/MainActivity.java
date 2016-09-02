package com.example.brijesh.myapplication1;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity
{

    int ii;

    @Override

    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toast.makeText(this,"Brijesh Prajapati",Toast.LENGTH_LONG).show();
        //int res=fun();
       // Toast.makeText(this,res,Toast.LENGTH_LONG).show();
    }
}
