package main

import (
	"database/sql"
	"fmt"

	"github.com/spiceai/gospice/v2"
	"github.com/spiceai/gospice/v2/pkg/function"
)

func HelloWorldGo(ctx *function.FunctionCtx, duckDb *sql.DB, client *gospice.SpiceClient) error {
	fmt.Println("Hello from Spice Go runtime!")

	// Temporary step
	_, err := duckDb.ExecContext(ctx, `
	create table output.ewgenius.demo.hello_world_golang (
		block_number bigint,
		greeting TEXT
	);`)
	if err != nil {
		return err
	}

	_, err = duckDb.ExecContext(ctx, "INSERT INTO output.ewgenius.demo.hello_world_golang (block_number, greeting) VALUES ($1, $2);", ctx.BlockNumber(), "Hello from Spice Go runtime!")
	if err != nil {
		return err
	}

	return nil
}

func main() {
	function.RunFunction(HelloWorldGo)
}